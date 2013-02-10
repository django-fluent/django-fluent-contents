from django.template import Library, Node, TemplateSyntaxError
from fluent_contents import rendering
from fluent_contents.plugins.sharedcontent.models import SharedContent
from fluent_contents.templatetags.placeholder_tags import get_request_var
from fluent_contents.utils.tagparsing import parse_token_kwargs

register = Library()


@register.tag
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
    """
    return SharedContentNode.parse(parser, token)


class SharedContentNode(Node):
    """
    The template node of the ``sharedplaceholder`` tag.
    """
    def __init__(self, slot_expr, template_expr):
        self.slot_expr = slot_expr
        self.template_expr = template_expr


    @classmethod
    def parse(cls, parser, token):
        """
        Parse the node syntax:

        .. code-block:: html+django

            {% sharedcontent slotname template="" %}
        """
        bits = token.split_contents()
        arg_bits, kwarg_bits = parse_token_kwargs(parser, bits, True, True, ('template',))

        if len(arg_bits) == 1:
            slot_expr = arg_bits[0]
        else:
            raise TemplateSyntaxError("""{0} tag allows one arguments: 'slot name' and optionally: template="..".""".format(bits[0]))

        template = kwarg_bits.pop('template', None)
        return cls(
            slot_expr=slot_expr,
            template_expr=template,
        )


    def render(self, context):
        request = get_request_var(context)

        # Get the placeholder
        slot = self.slot_expr.resolve(context)
        try:
            sharedcontent = SharedContent.objects.get(slug=slot)
        except SharedContent.DoesNotExist:
            return "<!-- shared content '{0}' does not yet exist -->".format(slot)

        template_name = self.template_expr.resolve(context) if self.template_expr else None
        return rendering.render_placeholder(request, sharedcontent.contents, sharedcontent, template_name=template_name)
