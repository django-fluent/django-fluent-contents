from django.core.cache import cache
from django.template import Library, TemplateSyntaxError
from django.contrib.sites.models import Site
from django.utils.translation import get_language
from fluent_contents import appsettings
from fluent_contents import rendering
from fluent_contents.plugins.sharedcontent.cache import get_shared_content_cache_key_ptr, get_shared_content_cache_key
from fluent_contents.plugins.sharedcontent.models import SharedContent
from tag_parser.basetags import BaseAssignmentOrOutputNode
from fluent_contents.utils.templatetags import is_true, extract_literal

register = Library()


@register.tag('sharedcontent')
def sharedcontent(parser, token):
    """
    Render a shared content block. Usage:

    .. code-block:: django+html

        {% sharedcontent "sidebar" %}

    Optionally, a template can be used to render the content items:

    .. code-block:: html+django

        {% sharedcontent "sidebar" template="mysite/parts/slot_placeholder.html" %}

    That template should loop over the content items, for example:

    .. code-block:: html+django

        {% for contentitem, html in contentitems %}
          {% if not forloop.first %}<div class="splitter"></div>{% endif %}
          {{ html }}
        {% endfor %}

    .. note::
       When a template is used, the system assumes that the output can change per request.
       Hence, the output of individual items will be cached, but the final merged output is no longer cached.
       Add ``cachable=1`` to enable output caching for templates too.
    """
    return SharedContentNode.parse(parser, token)


class SharedContentNode(BaseAssignmentOrOutputNode):

    min_args = 1
    max_args = 1
    allowed_kwargs = ('template', 'cachable')

    @classmethod
    def validate_args(cls, tag_name, *args, **kwargs):
        if len(args) != 1:
            raise TemplateSyntaxError("""{0} tag allows one arguments: 'slot name' and optionally: template="..".""".format(tag_name))

        super(SharedContentNode, cls).validate_args(tag_name, *args)

    def get_value(self, context, *tag_args, **tag_kwargs):
        request = self.get_request(context)
        output = None

        # Process arguments
        (slot,) = tag_args
        template_name = tag_kwargs.get('template') or None
        cachable = is_true(tag_kwargs.get('cachable', not bool(template_name)))  # default: True unless there is a template.

        if template_name and cachable and not extract_literal(self.kwargs['template']):
            # If the template name originates from a variable, it can change any time.
            # See PagePlaceholderNode.render_tag() why this is not allowed.
            raise TemplateSyntaxError("{0} tag does not allow 'cachable' for variable template names!".format(self.tag_name))

        # Caching will not happen when rendering via a template,
        # because there is no way to tell whether that can be expired/invalidated.
        try_cache = appsettings.FLUENT_CONTENTS_CACHE_OUTPUT \
                and appsettings.FLUENT_CONTENTS_CACHE_PLACEHOLDER_OUTPUT \
                and cachable

        if isinstance(slot, SharedContent):
            # Allow passing a sharedcontent, just like 'render_placeholder' does.
            sharedcontent = slot

            # See if there is cached output, avoid fetching the Placeholder via sharedcontents.contents.
            if try_cache:
                cache_key = get_shared_content_cache_key(sharedcontent)
                output = cache.get(cache_key)
        else:
            site = Site.objects.get_current()
            if try_cache:
                # See if there is output cached, try to avoid fetching the SharedContent + Placeholder model.
                # Have to perform 2 cache calls for this, because the placeholder output key is based on object IDs
                cache_key_ptr = get_shared_content_cache_key_ptr(int(site.pk), slot, language_code=get_language())
                cache_key = cache.get(cache_key_ptr)
                if cache_key is not None:
                    output = cache.get(cache_key)

            if output is None:
                # Get the placeholder
                try:
                    sharedcontent = SharedContent.objects.parent_site(site).get(slug=slot)
                except SharedContent.DoesNotExist:
                    return "<!-- shared content '{0}' does not yet exist -->".format(slot)

                # Now that we've fetched the object, the object key be generated.
                # No real need to check for output again, render_placeholder() does that already.
                if try_cache and not cache_key:
                    cache.set(cache_key_ptr, get_shared_content_cache_key(sharedcontent))

        if output is None:
            # Have to fetch + render it.
            output = self.render_shared_content(request, sharedcontent, template_name, cachable=cachable)

        rendering.register_frontend_media(request, output.media)  # Need to track frontend media here, as the template tag can't return it.
        return output.html

    def render_shared_content(self, request, sharedcontent, template_name=None, cachable=None):
        # All parsing done, perform the actual rendering
        placeholder = sharedcontent.contents  # Another DB query
        return rendering.render_placeholder(request, placeholder, sharedcontent,
            template_name=template_name,
            cachable=cachable,
            fallback_language=True
        )
