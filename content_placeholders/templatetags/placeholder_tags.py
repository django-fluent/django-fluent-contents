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
    try:
        (tag_name, parent_object_var_name, placeholder_var_name) = token.split_contents()
    except ValueError:
        raise TemplateSyntaxError, "%r tag requires a two arguments: parent-object placeholder-name" % token.contents.split()[0]
    return PlaceholderNode(parent_object_var_name, placeholder_var_name)


class PlaceholderNode(Node):
    """
    Template Node for a region.
    """
    def __init__(self, parent_var_name, placeholder_var_name):
        self.parent_var_name = parent_var_name
        self.placeholder_var_name = placeholder_var_name

    def render(self, context):
        request = _get_request(context)

        # Get the placeholder
        parent = Variable(self.parent_var_name).resolve(context)
        slot = Variable(self.placeholder_var_name).resolve(context)
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
