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
from django.utils.safestring import SafeData
from fluent_contents.models import Placeholder, ImmutableMedia
from fluent_contents import rendering
from tag_parser import parse_token_kwargs
from tag_parser.basetags import BaseNode

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
    """
    return PagePlaceholderNode.parse(parser, token)


class PagePlaceholderNode(BaseNode):
    """
    The template node of the ``page_placeholder`` tag.
    It renders a placeholder of a provided parent object.
    The template tag can also contain additional metadata,
    which can be returned by scanning for this node using the :ref:`fluent_contents.analyzer` module.
    """
    allowed_kwargs = ('title', 'role', 'template', 'fallback')
    min_args = 1
    max_args = 2


    def __init__(self, tag_name, parent_expr, slot_expr, template_expr, fallback_expr, meta_kwargs):
        super(PagePlaceholderNode, self).__init__(tag_name, parent_expr, slot_expr, template=template_expr, **meta_kwargs)

        self.parent_expr = parent_expr
        self.slot_expr = slot_expr
        self.template_expr = template_expr
        self.fallback_expr = fallback_expr
        self.meta_kwargs = meta_kwargs


    @classmethod
    def parse(cls, parser, token):
        """
        Parse the node syntax:

        .. code-block:: html+django

            {% page_placeholder parentobj slotname title="test" role="m" %}
        """
        tag_name, args, kwargs = parse_token_kwargs(parser, token, allowed_kwargs=cls.allowed_kwargs, compile_args=True, compile_kwargs=True)

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

        template_expr = kwargs.pop('template', None)
        fallback_expr = kwargs.pop('fallback', None)
        return cls(
            tag_name=tag_name,
            parent_expr=parent_expr,
            slot_expr=slot_expr,
            template_expr=template_expr,
            fallback_expr=fallback_expr,
            meta_kwargs=kwargs  # The remaining non-functional args for CMS admin page.
        )


    def get_slot(self):
        """
        Return the string literal that is used for the placeholder slot in the template.
        When the variable is not a string literal, ``None`` is returned.
        """
        return self._extract_literal(self.slot_expr)


    def _extract_literal(self, templatevar):
        # FilterExpression contains another 'var' that either contains a Variable or SafeData object.
        if hasattr(templatevar, 'var'):
            templatevar = templatevar.var
            if isinstance(templatevar, SafeData):
                # Literal in FilterExpression, can return.
                return templatevar
            else:
                # Variable in FilterExpression, not going to work here.
                return None

        if templatevar[0] in ('"', "'") and templatevar[-1] in ('"', "'"):
            return templatevar[1:-1]
        else:
            return None


    def _extract_bool(self, templatevar):
        # FilterExpression contains another 'var' that either contains a Variable or SafeData object.
        if hasattr(templatevar, 'var'):
            templatevar = templatevar.var
            if isinstance(templatevar, SafeData):
                # Literal in FilterExpression, can return.
                return templatevar
            else:
                # Variable in FilterExpression, not going to work here.
                return None

        return self._is_true(templatevar)


    def _is_true(self, value):
        return value in (1, '1', 'true', 'True', True)


    def get_title(self):
        """
        Return the string literal that is used in the template.
        The title is used in the admin screens.
        """
        try:
            return self._extract_literal(self.meta_kwargs['title'])
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
            return self._extract_literal(self.meta_kwargs['role'])
        except KeyError:
            return None


    def get_fallback_language(self):
        """
        Return whether to use the fallback language.
        """
        try:
            # Note: currently not supporting strings yet.
            return self._extract_bool(self.fallback_expr) or None
        except KeyError:
            return False


    def render(self, context):
        request = self.get_request(context)

        # Get the placeholder
        parent = self.parent_expr.resolve(context)
        slot = self.slot_expr.resolve(context)
        fallback_language = self._is_true(self.fallback_expr.resolve(context)) if self.fallback_expr else False
        try:
            placeholder = Placeholder.objects.get_by_slot(parent, slot)
        except Placeholder.DoesNotExist:
            return "<!-- placeholder '{0}' does not yet exist -->".format(slot)

        template_name = self.template_expr.resolve(context) if self.template_expr else None

        output = rendering.render_placeholder(request, placeholder, parent, template_name=template_name, fallback_language=fallback_language)
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


class RenderPlaceholderNode(BaseNode):
    """
    The template node of the ``render_placeholder`` tag.
    It renders the provided placeholder object.
    """
    min_args = 1
    max_args = 1

    @classmethod
    def validate_args(cls, tag_name, *args, **kwargs):
        if len(args) != 1:
            raise TemplateSyntaxError("""{0} tag allows only one parameter: a placeholder object.""".format(tag_name))

        super(RenderPlaceholderNode, cls).validate_args(tag_name, *args, **kwargs)


    def render_tag(self, context, *tag_args, **tag_kwargs):
        request = self.get_request(context)

        try:
            placeholder = _get_placeholder_arg(self.args[0], tag_args[0])
        except RuntimeWarning as e:
            return u"<!-- {0} -->".format(e)

        # To support filtering the placeholders by parent language, the parent object needs to be known.
        # Fortunately, the PlaceholderFieldDescriptor makes sure this doesn't require an additional query.
        parent_object = placeholder.parent

        output = rendering.render_placeholder(request, placeholder, parent_object)
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
        try:
            return placeholder.all()[0]
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
