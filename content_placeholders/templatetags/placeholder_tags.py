from django.template import Library, Node, TemplateSyntaxError
from django.utils.safestring import SafeUnicode
from content_placeholders.models import Placeholder
from content_placeholders import rendering
import re

register = Library()

kwarg_re = re.compile('^(?P<name>\w+)=')

def _split_token_args(bits, parser, compile_args=False, compile_kwargs=False):
    expect_kwarg = False
    args = []
    kwargs = {}
    prev_bit = None
    for bit in bits[1::]:
        match = kwarg_re.match(bit)
        if match:
            expect_kwarg = True
            (name, expr) = bit.split('=', 2)
            kwargs[name] = parser.compile_filter(expr) if compile_args else expr
        else:
            if expect_kwarg:
                raise TemplateSyntaxError("{0} tag may not have a non-keyword argument ({1}) after a keyword argument ({2}).".format(bits[0], bit, prev_bit))
            args.append(parser.compile_filter(bit) if compile_kwargs else bit)

        prev_bit = bit

    return args, kwargs


@register.tag
def render_placeholder(parser, token):
    """
    Render a placeholder for a given object.
    Example::

        {% render_placeholder currentpage "slotname" %}
    """
    bits = token.split_contents()
    arg_bits, kwarg_bits = _split_token_args(bits, parser)

    if len(arg_bits) == 2:
        (parent, slot) = arg_bits
        return PagePlaceholderNode(
            parent_expr=parser.compile_filter(parent),
            slot_expr=parser.compile_filter(slot),
            meta_kwargs=kwarg_bits
        )
    else:
        raise TemplateSyntaxError("""{0} tag allows two arguments: 'slotname' 'parent-object' and optionally: title=".." role="..".""".format(bits[0]))


class PlaceholderNode(Node):
    """
    Template Node for a placeholder.
    """
    def __init__(self, parent_expr, slot_expr, meta_kwargs):
        self.parent_expr = parent_expr
        self.slot_expr = slot_expr
        self.kwargs = meta_kwargs

        for key in meta_kwargs.keys():
            if key not in ('title', 'role'):
                raise TemplateSyntaxError("Unsupported meta argument: {0}".format(key))


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
        # TODO: stub, return title from template
        if self.kwargs.has_key('title'):
            return self._extract_literal(self.kwargs['title'])

        slot = self.get_slot()
        if slot is not None:
            return slot.capitalize()

        return None


    def get_role(self):
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

        return rendering.render_placeholder(request, placeholder, parent)


def _get_request(context):
    """
    Fetch the request from the context.

    This enforces the use of a RequestProcessor, e.g.

        render_to_response("page.html", context, context_instance=RequestContext(request))
    """
    # This error message is issued to help newcomers find solutions faster!
    assert context.has_key('request'), "The placeholder functions require a 'request' object in the context, is 'RequestContext' not used or 'TEMPLATE_CONTEXT_PROCESSORS' not defined?"
    return context['request']
