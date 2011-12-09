from django.template import Library, Node, Variable, TemplateSyntaxError
from content_placeholders.models import Placeholder
from content_placeholders import rendering

register = Library()


@register.tag
def render_placeholder(parser, token):
    """
    Render a placeholder for a given object.
    Example::

        {% render_placeholder currentpage "slotname" %}
    """
    bits = token.split_contents()
    if len(bits) == 3:
        (tag_name, parent_object_var_name, slot_var_name) = bits
        return PlaceholderNode(parent_object_var_name, slot_var_name)
    else:
        raise TemplateSyntaxError, "{0} tag requires 2 arguments: parent-object placeholder-name".format(bits[0])


class PlaceholderNode(Node):
    """
    Template Node for a placeholder.
    """
    def __init__(self, parent_var_name, slot_var_name):
        self.parent_var = Variable(parent_var_name)
        self.slot_var = Variable(slot_var_name)


    def get_slot(self):
        """
        Return the string literal that is used for the placeholder slot in the template.
        When the variable is not a string literal, ``None`` is returned.
        """
        literal = self.slot_var.var
        if literal[0] in ('"', "'") and literal[-1] in ('"', "'"):
            return literal[1:-1]
        else:
            return None


    def get_title(self):
        # TODO: stub, return title from template
        slot = self.get_slot()
        if slot is None:
            return ''
        else:
            return slot.capitalize()


    def render(self, context):
        request = _get_request(context)

        # Get the placeholder
        parent = self.parent_var.resolve(context)
        slot = self.slot_var.resolve(context)
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
