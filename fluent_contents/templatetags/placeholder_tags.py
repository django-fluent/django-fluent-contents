"""
The ``placeholder_tags`` module provides two template tags for rendering placeholders:
It can be loaded using:

.. code-block:: html+django

    {% load placeholder_tags %}

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
from django.db.models import Manager
from django.template import Library, Node, Variable, TemplateSyntaxError
from django.utils.safestring import SafeUnicode
from fluent_contents.models import Placeholder
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
    allowed_kwargs = ('title', 'role', 'template',)
    min_args = 1
    max_args = 2


    def __init__(self, tag_name, parent_expr, slot_expr, template_expr, meta_kwargs):
        super(PagePlaceholderNode, self).__init__(tag_name, parent_expr, slot_expr, template=template_expr, **meta_kwargs)

        self.parent_expr = parent_expr
        self.slot_expr = slot_expr
        self.template_expr = template_expr
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
        return cls(
            tag_name=tag_name,
            parent_expr=parent_expr,
            slot_expr=slot_expr,
            template_expr=template_expr,
            meta_kwargs=kwargs
        )


    def get_slot(self):
        """
        Return the string literal that is used for the placeholder slot in the template.
        When the variable is not a string literal, ``None`` is returned.
        """
        return self._extract_literal(self.slot_expr)


    def _extract_literal(self, templatevar):
        # FilterExpression contains another 'var' that either contains a Variable or SafeUnicode object.
        if hasattr(templatevar, 'var'):
            templatevar = templatevar.var
            if isinstance(templatevar, SafeUnicode):
                # Literal in FilterExpression, can return.
                return templatevar
            else:
                # Variable in FilterExpression, not going to work here.
                return None

        if templatevar[0] in ('"', "'") and templatevar[-1] in ('"', "'"):
            return templatevar[1:-1]
        else:
            return None


    def get_title(self):
        """
        Return the string literal that is used in the template.
        The title is used in the admin screens.
        """
        if self.meta_kwargs.has_key('title'):
            return self._extract_literal(self.meta_kwargs['title'])

        slot = self.get_slot()
        if slot is not None:
            return slot.replace('_', ' ').title()

        return None


    def get_role(self):
        """
        Return the string literal that is used in the template.
        The role can be "main", "sidebar" or "related", or shorted to "m", "s", "r".
        """
        if self.meta_kwargs.has_key('role'):
            return self._extract_literal(self.meta_kwargs['role'])
        else:
            return None


    def render(self, context):
        request = self.get_request(context)

        # Get the placeholder
        parent = self.parent_expr.resolve(context)
        slot = self.slot_expr.resolve(context)
        try:
            placeholder = Placeholder.objects.get_by_slot(parent, slot)
        except Placeholder.DoesNotExist:
            return "<!-- placeholder '{0}' does not yet exist -->".format(slot)

        template_name = self.template_expr.resolve(context) if self.template_expr else None
        return rendering.render_placeholder(request, placeholder, parent, template_name=template_name)


@register.tag
def render_placeholder(parser, token):
    """
    Render a shared placeholder. Syntax:

    .. code-block:: html+django

        {% render_placeholder "slotname" %}{# for global objects. #}
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
            raise TemplateSyntaxError("""{0} tag allows only one parameter: 'slotname'.""".format(tag_name))

        super(RenderPlaceholderNode, cls).validate_args(tag_name, *args, **kwargs)


    def render_tag(self, context, *tag_args, **tag_kwargs):
        request = self.get_request(context)
        (placeholder,) = tag_args

        if placeholder is None:
            return "<!-- placeholder object is None -->"
        elif isinstance(placeholder, Placeholder):
            pass
        elif isinstance(placeholder, basestring):
            # This feature only exists at database level, the "sharedcontent" plugin solves this issue.
            slot = placeholder
            try:
                placeholder = Placeholder.objects.get_by_slot(None, slot)
            except Placeholder.DoesNotExist:
                return "<!-- global placeholder '{0}' does not yet exist -->".format(slot)
        elif isinstance(placeholder, Manager):
            try:
                placeholder = placeholder.all()[0]
            except IndexError:
                return "<!-- No placeholders found for query -->".format(self.args[0])
        else:
            raise ValueError("The field '{0}' does not refer to a placeholder or slotname!".format(self.args[0]))

        return rendering.render_placeholder(request, placeholder)
