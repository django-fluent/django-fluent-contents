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
from fluent_contents.utils.tagparsing import parse_token_kwargs

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


class PagePlaceholderNode(Node):
    """
    The template node of the ``page_placeholder`` tag.
    It renders a placeholder of a provided parent object.
    The template tag can also contain additional metadata,
    which can be returned by scanning for this node using the :ref:`fluent_contents.analyzer` module.
    """
    def __init__(self, parent_expr, slot_expr, template_expr, meta_kwargs):
        self.parent_expr = parent_expr
        self.slot_expr = slot_expr
        self.template_expr = template_expr
        self.kwargs = meta_kwargs


    @classmethod
    def parse(cls, parser, token):
        """
        Parse the node syntax:

        .. code-block:: html+django

            {% page_placeholder parentobj slotname title="test" role="m" %}
        """
        bits = token.split_contents()
        arg_bits, kwarg_bits = parse_token_kwargs(parser, bits, True, True, ('title', 'role', 'template'))

        if len(arg_bits) == 2:
            (parent_expr, slot_expr) = arg_bits
        elif len(arg_bits) == 1:
            # Allow 'page' by default. Works with most CMS'es, including django-fluent-pages.
            (parent_expr, slot_expr) = (Variable('page'), arg_bits[0])
        else:
            raise TemplateSyntaxError("""{0} tag allows two arguments: 'parent object' 'slot name' and optionally: title=".." role="..".""".format(bits[0]))

        template = kwarg_bits.pop('template', None)
        return cls(
            parent_expr=parent_expr,
            slot_expr=slot_expr,
            template_expr=template,
            meta_kwargs=kwarg_bits
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
        if self.kwargs.has_key('title'):
            return self._extract_literal(self.kwargs['title'])

        slot = self.get_slot()
        if slot is not None:
            return slot.replace('_', ' ').title()

        return None


    def get_role(self):
        """
        Return the string literal that is used in the template.
        The role can be "main", "sidebar" or "related", or shorted to "m", "s", "r".
        """
        if self.kwargs.has_key('role'):
            return self._extract_literal(self.kwargs['role'])
        else:
            return None


    def render(self, context):
        request = _get_request(context)

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


class RenderPlaceholderNode(Node):
    """
    The template node of the ``render_placeholder`` tag.
    It renders the provided placeholder object.
    """
    def __init__(self, placeholder_expr):
        self.placeholder_expr = placeholder_expr


    @classmethod
    def parse(cls, parser, token):
        bits = token.split_contents()
        if len(bits) == 2:
            return cls(
                placeholder_expr=parser.compile_filter(bits[1])
            )
        else:
            raise TemplateSyntaxError("""{0} tag allows only one parameter: 'slotname'.""".format(bits[0]))


    def render(self, context):
        request = _get_request(context)
        placeholder = self.placeholder_expr.resolve(context)

        if placeholder is None:
            return "<!-- placeholder object is None -->"
        elif isinstance(placeholder, Placeholder):
            pass
        elif isinstance(placeholder, basestring):
            slot = placeholder
            try:
                placeholder = Placeholder.objects.get_by_slot(None, slot)
            except Placeholder.DoesNotExist:
                return "<!-- global placeholder '{0}' does not yet exist -->".format(slot)
        elif isinstance(placeholder, Manager):
            try:
                placeholder = placeholder.all()[0]
            except IndexError:
                return "<!-- No placeholders found for query -->".format(self.placeholder_expr)
        else:
            raise ValueError("The field '{0}' does not refer to a placeholder or slotname!".format(self.placeholder_expr))

        return rendering.render_placeholder(request, placeholder)


def _get_request(context):
    """
    Fetch the request from the context.

    This enforces the use of a RequestProcessor, e.g.

        render_to_response("page.html", context, context_instance=RequestContext(request))
    """
    # This error message is issued to help newcomers find solutions faster!
    assert context.has_key('request'), "The placeholder functions require a 'request' object in the context, is 'RequestContext' not used or 'TEMPLATE_CONTEXT_PROCESSORS' not defined?"
    return context['request']
