"""
The ``fluent_contents_tags`` module provides two template tags for rendering placeholders:
It can be loaded using:

.. code-block:: html+django

    {% load fluent_contents_tags %}

A placeholder which is stored in a :class:`~fluent_contents.models.PlaceholderField` can
be rendered with the following syntax:

.. code-block:: html+django

    {% render_placeholder someobject.placeholder %}

To support CMS interfaces, placeholder slots can be defined in the template.
This is done using the following syntax:

.. code-block:: html+django

    {% page_placeholder currentpage "slotname" %}
    {% page_placeholder currentpage "slotname" title="Admin title" role="main" %}

The CMS interface can scan for those tags using the :ref:`fluent_contents.analyzer` module.
"""
import six

from django.conf import settings
from django.db.models import Manager
from django.forms import Media
from django.template import Library, Variable, TemplateSyntaxError
from fluent_contents.models import Placeholder, ImmutableMedia
from fluent_contents import rendering
from tag_parser import parse_token_kwargs, parse_as_var
from tag_parser.basetags import BaseNode, BaseAssignmentOrOutputNode
from fluent_contents import appsettings
from fluent_contents.rendering import get_cached_placeholder_output
from fluent_contents.utils.templatetags import is_true, extract_literal, extract_literal_bool

register = Library()


@register.tag
def page_placeholder(parser, token):
    """
    Render a placeholder for a given object. Syntax:

    .. code-block:: html+django

        {% page_placeholder currentpage "slotname"  %}

    Additionally, extra meta information can be provided for the admin interface.

    .. code-block:: html+django

        {% page_placeholder currentpage "slotname" title="Tab title" role="main %}

    If the currentpage variable is named ``page``, it can be left out.

    The extra information can be extracted with the
    :func:`~PagePlaceholderNode.get_title` and :func:`~PagePlaceholderNode.get_role`
    functions of the :class:`~PagePlaceholderNode` class.

    Optionally, a template can be used to render the placeholder:

    .. code-block:: html+django

        {% page_placeholder currentpage "slotname" template="mysite/parts/slot_placeholder.html" %}

    That template should loop over the content items, for example:

    .. code-block:: html+django

        {% for contentitem, html in contentitems %}
          {% if not forloop.first %}<div class="splitter"></div>{% endif %}
          {{ html }}
        {% endfor %}

    .. note::
       When a template is used, the system assumes that the output can change per request.
       Hence, the output of individual items will be cached, but the final merged output is no longer cached.
       Add ``cachable=True`` to enable output caching for templates too.
    """
    return PagePlaceholderNode.parse(parser, token)


class PagePlaceholderNode(BaseAssignmentOrOutputNode):
    """
    The template node of the ``page_placeholder`` tag.
    It renders a placeholder of a provided parent object.
    The template tag can also contain additional metadata,
    which can be returned by scanning for this node using the :ref:`fluent_contents.analyzer` module.
    """
    allowed_kwargs = ('title', 'role', 'template', 'cachable', 'fallback')
    allowed_meta_kwargs = ('title', 'role')
    min_args = 1
    max_args = 2

    def __init__(self, tag_name, as_var, parent_expr, slot_expr, **kwargs):
        super(PagePlaceholderNode, self).__init__(tag_name, as_var, parent_expr, slot_expr, **kwargs)
        self.slot_expr = slot_expr

        # Move some arguments outside the regular "kwargs"
        # because they don't need to be parsed as variables.
        # Those are the remaining non-functional args for CMS admin page.
        self.meta_kwargs = {}
        for arg in self.allowed_meta_kwargs:
            try:
                self.meta_kwargs[arg] = kwargs.pop(arg)
            except KeyError:
                pass

    @classmethod
    def parse(cls, parser, token):
        """
        Parse the node syntax:

        .. code-block:: html+django

            {% page_placeholder parentobj slotname title="test" role="m" %}
        """
        bits, as_var = parse_as_var(parser, token)
        tag_name, args, kwargs = parse_token_kwargs(parser, bits, allowed_kwargs=cls.allowed_kwargs, compile_args=True, compile_kwargs=True)

        # Play with the arguments
        if len(args) == 2:
            parent_expr = args[0]
            slot_expr = args[1]
        elif len(args) == 1:
            # Allow 'page' by default. Works with most CMS'es, including django-fluent-pages.
            parent_expr = Variable('page')
            slot_expr = args[0]
        else:
            raise TemplateSyntaxError("""{0} tag allows two arguments: 'parent object' 'slot name' and optionally: title=".." role="..".""".format(tag_name))

        cls.validate_args(tag_name, *args, **kwargs)
        return cls(
            tag_name=tag_name,
            as_var=as_var,
            parent_expr=parent_expr,
            slot_expr=slot_expr,
            **kwargs
        )

    def get_slot(self):
        """
        Return the string literal that is used for the placeholder slot in the template.
        When the variable is not a string literal, ``None`` is returned.
        """
        return extract_literal(self.slot_expr)

    def get_title(self):
        """
        Return the string literal that is used in the template.
        The title is used in the admin screens.
        """
        try:
            return extract_literal(self.meta_kwargs['title'])
        except KeyError:
            slot = self.get_slot()
            if slot is not None:
                return slot.replace('_', ' ').title()

            return None

    def get_role(self):
        """
        Return the string literal that is used in the template.
        The role can be "main", "sidebar" or "related", or shorted to "m", "s", "r".
        """
        try:
            return extract_literal(self.meta_kwargs['role'])
        except KeyError:
            return None

    def get_fallback_language(self):
        """
        Return whether to use the fallback language.
        """
        try:
            # Note: currently not supporting strings yet.
            return extract_literal_bool(self.kwargs['fallback']) or None
        except KeyError:
            return False

    def get_value(self, context, *tag_args, **tag_kwargs):
        request = self.get_request(context)
        output = None

        # Process arguments
        parent, slot = tag_args
        template_name = tag_kwargs.get('template', None)
        cachable = is_true(tag_kwargs.get('cachable', not bool(template_name)))  # default: True unless there is a template.
        fallback_language = is_true(tag_kwargs.get('fallback', False))

        if template_name and cachable and not extract_literal(self.kwargs['template']):
            # If the template name originates from a variable, it can change any time.
            # It's not possible to create a reliable output cache for for that,
            # as it would have to include any possible template name in the key.
            raise TemplateSyntaxError("{0} tag does not allow 'cachable' for variable template names!".format(self.tag_name))

        if appsettings.FLUENT_CONTENTS_CACHE_OUTPUT \
        and appsettings.FLUENT_CONTENTS_CACHE_PLACEHOLDER_OUTPUT \
        and cachable:
            # See if the entire placeholder output is cached,
            # if so, no database queries have to be performed.
            # This will be omitted when an template is used,
            # because there is no way to expire that or tell whether that template is cacheable.
            output = get_cached_placeholder_output(parent, slot)

        if output is None:
            # Get the placeholder
            try:
                placeholder = Placeholder.objects.get_by_slot(parent, slot)
            except Placeholder.DoesNotExist:
                return "<!-- placeholder '{0}' does not yet exist -->".format(slot)

            output = rendering.render_placeholder(request, placeholder, parent,
                template_name=template_name,
                cachable=cachable,
                limit_parent_language=True,
                fallback_language=fallback_language
            )

        rendering.register_frontend_media(request, output.media)   # Assume it doesn't hurt. TODO: should this be optional?
        return output.html


@register.tag
def render_placeholder(parser, token):
    """
    Render a shared placeholder. Syntax:

    .. code-block:: html+django

        {% render_placeholder someobject.placeholder %}
    """
    return RenderPlaceholderNode.parse(parser, token)


class RenderPlaceholderNode(BaseAssignmentOrOutputNode):
    """
    The template node of the ``render_placeholder`` tag.
    It renders the provided placeholder object.
    """
    min_args = 1
    max_args = 1
    allowed_kwargs = ('template', 'cachable', 'fallback')

    @classmethod
    def validate_args(cls, tag_name, *args, **kwargs):
        if len(args) != 1:
            raise TemplateSyntaxError("""{0} tag allows only one parameter: a placeholder object.""".format(tag_name))

        super(RenderPlaceholderNode, cls).validate_args(tag_name, *args, **kwargs)

    def get_value(self, context, *tag_args, **tag_kwargs):
        request = self.get_request(context)

        # Parse arguments
        try:
            placeholder = _get_placeholder_arg(self.args[0], tag_args[0])
        except RuntimeWarning as e:
            return u"<!-- {0} -->".format(e)

        template_name = tag_kwargs.get('template', None)
        cachable = is_true(tag_kwargs.get('cachable', not bool(template_name)))  # default: True unless there is a template.
        fallback_language = is_true(tag_kwargs.get('fallback', False))

        if template_name and cachable and not extract_literal(self.kwargs['template']):
            # If the template name originates from a variable, it can change any time.
            # See PagePlaceholderNode.render_tag() why this is not allowed.
            raise TemplateSyntaxError("{0} tag does not allow 'cachable' for variable template names!".format(self.tag_name))

        # Fetching placeholder.parent should not cause queries if fetched via PlaceholderFieldDescriptor.
        # See render_placeholder() for more details
        output = rendering.render_placeholder(request, placeholder, placeholder.parent,
            template_name=template_name,
            cachable=cachable,
            limit_parent_language=True,
            fallback_language=fallback_language
        )
        rendering.register_frontend_media(request, output.media)   # Need to track frontend media here, as the template tag can't return it.
        return output.html


def _get_placeholder_arg(arg_name, placeholder):
    """
    Validate and return the Placeholder object that the template variable points to.
    """
    if placeholder is None:
        raise RuntimeWarning(u"placeholder object is None")
    elif isinstance(placeholder, Placeholder):
        return placeholder
    elif isinstance(placeholder, Manager):
        manager = placeholder
        try:
            parent_object = manager.instance  # read RelatedManager code
        except AttributeError:
            parent_object = None

        try:
            placeholder = manager.all()[0]
            if parent_object is not None:
                placeholder.parent = parent_object  # Fill GFK cache
            return placeholder
        except IndexError:
            raise RuntimeWarning(u"No placeholders found for query '{0}.all.0'".format(arg_name))
    else:
        raise ValueError(u"The field '{0}' does not refer to a placeholder object!".format(arg_name))


@register.tag
def render_content_items_media(parser, token):
    """
    Render the JS/CSS includes for the media which was collected during the handling of the request.
    This tag should be placed at the bottom of the page.

    .. code-block:: html+django

        {% render_content_items_media %}
        {% render_content_items_media css %}
        {% render_content_items_media js %}
        {% render_content_items_media js local %}
        {% render_content_items_media js external %}
    """
    return RenderContentItemsMedia.parse(parser, token)


class RenderContentItemsMedia(BaseNode):
    """
    The template node of the ``render_plugin_media`` tag.
    It renders the media object object.
    """
    compile_args = False
    compile_kwargs = False
    min_args = 0
    max_args = 2

    @classmethod
    def validate_args(cls, tag_name, *args, **kwargs):
        super(RenderContentItemsMedia, cls).validate_args(tag_name, *args, **kwargs)
        if args:
            if args[0] not in ('css', 'js'):
                raise TemplateSyntaxError("'{0}' tag only supports `css` or `js` as first argument".format(tag_name))
            if len(args) > 1 and args[1] not in ('local', 'external'):
                raise TemplateSyntaxError("'{0}' tag only supports `local` or `external` as second argument".format(tag_name))

    def render_tag(self, context, media_type=None, domain=None):
        request = self.get_request(context)

        media = rendering.get_frontend_media(request)
        if not media or not (media._js or media._css):
            return u''

        if not media_type:
            return media.render()
        elif media_type == 'js':
            if domain:
                media = _split_js(media, domain)
            return u'\n'.join(media.render_js())
        elif media_type == 'css':
            if domain:
                media = _split_css(media, domain)
            return u'\n'.join(media.render_css())
        else:
            return ''


if settings.STATIC_URL is None:
    _LOCAL_PREFIX = settings.MEDIA_URL  # backwards compatibility
else:
    _LOCAL_PREFIX = settings.STATIC_URL


def _is_local(url):
    # URL can be http:// if that's what's also in STATIC_URL.
    # Otherwise, the domain is external.
    return not url.startswith(('//', 'http://', 'https://')) or url.startswith(_LOCAL_PREFIX)


def _split_js(media, domain):
    """
    Extract the local or external URLs from a Media object.
    """
    # Read internal property without creating new Media instance.
    if not media._js:
        return ImmutableMedia.empty_instance

    needs_local = domain == 'local'
    new_js = []
    for url in media._js:
        if needs_local == _is_local(url):
            new_js.append(url)

    if not new_js:
        return ImmutableMedia.empty_instance
    else:
        return Media(js=new_js)


def _split_css(media, domain):
    """
    Extract the local or external URLs from a Media object.
    """
    # Read internal property without creating new Media instance.
    if not media._css:
        return ImmutableMedia.empty_instance

    needs_local = domain == 'local'
    new_css = {}
    for medium, url in six.iteritems(media._css):
        if needs_local == _is_local(url):
            new_css.setdefault(medium, []).append(url)

    if not new_css:
        return ImmutableMedia.empty_instance
    else:
        return Media(css=new_css)
