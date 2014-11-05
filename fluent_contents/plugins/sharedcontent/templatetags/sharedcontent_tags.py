from django.template import Library, TemplateSyntaxError
from django.contrib.sites.models import Site
from fluent_contents import rendering
from fluent_contents.plugins.sharedcontent.models import SharedContent
from tag_parser import template_tag
from tag_parser.basetags import BaseNode

register = Library()


@template_tag(register, 'sharedcontent')
class SharedContentNode(BaseNode):
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
    """
    min_args = 1
    max_args = 1
    allowed_kwargs = ('template',)


    @classmethod
    def validate_args(cls, tag_name, *args, **kwargs):
        if len(args) != 1:
            raise TemplateSyntaxError("""{0} tag allows one arguments: 'slot name' and optionally: template="..".""".format(tag_name))

        super(SharedContentNode, cls).validate_args(tag_name, *args)


    def render_tag(self, context, *tag_args, **tag_kwargs):
        request = self.get_request(context)
        (slot,) = tag_args

        if isinstance(slot, SharedContent):
            # Allow passing a sharedcontent, just like 'render_placeholder' does.
            sharedcontent = slot
        else:
            # Get the placeholder
            try:
                site = Site.objects.get_current()
                sharedcontent = SharedContent.objects.parent_site(site).get(slug=slot)
            except SharedContent.DoesNotExist:
                return "<!-- shared content '{0}' does not yet exist -->".format(slot)

        template_name = tag_kwargs.get('template') or None
        return self.render_shared_content(request, sharedcontent, template_name)

    def render_shared_content(self, request, sharedcontent, template_name):
        # All parsing done, perform the actual rendering
        output = rendering.render_placeholder(request, sharedcontent.contents, sharedcontent, template_name=template_name, fallback_language=True)
        rendering.register_frontend_media(request, output.media)  # Need to track frontend media here, as the template tag can't return it.
        return output.html
