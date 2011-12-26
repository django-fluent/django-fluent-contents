from django.template import Library, Node
from django.template.base import TemplateSyntaxError
from fluent_contents.admin.contentitems import GenericContentItemInline

register = Library()

@register.filter
def only_content_item_inlines(inlines):
    return [i for i in inlines if isinstance(i, GenericContentItemInline)]


@register.filter
def only_content_item_formsets(formsets):
    return [f for f in formsets if isinstance(f.opts, GenericContentItemInline)]


@register.filter
def group_plugins_into_categories(plugins):
    """
    Return all plugins, grouped by category.
    The structure is a {"Categorynane": [list of plugin classes]}
    """
    if not plugins:
        return {}
    plugins = sorted(plugins, key=lambda p: p.verbose_name)
    categories = {}

    for plugin in plugins:
        title = unicode(plugin.category or u"")  # enforce resolving ugettext_lazy proxies.
        if not categories.has_key(title):
            categories[title] = []
        categories[title].append(plugin)

    return categories


@register.filter
def plugin_categories_to_list(plugin_categories):
    if not plugin_categories:
        return []
    categories_list = plugin_categories.items()
    categories_list.sort(key=lambda item: item[0])  # sort category names
    return categories_list


@register.filter
def plugin_categories_to_choices(categories):
    """
    Return a tuple of plugin model choices, suitable for a select field.
    Each tuple is a ("TypeName", "Title") value.
    """
    choices = []
    for category, items in categories.iteritems():
        if items:
            plugin_tuples = tuple((plugin.type_name, plugin.verbose_name) for plugin in items)
            if category:
                choices.append((category, plugin_tuples))
            else:
                choices += plugin_tuples

    choices.sort(key=lambda item: item[0])
    return choices


class GetFirstOfNode(Node):
    def __init__(self, filters, var_name):
        self.filters = filters    # list of FilterExpression nodes.
        self.var_name = var_name

    def render(self, context):
        value = None
        for filter in self.filters:
            # The ignore_failures argument is the most important, otherwise
            # the value is converted to the TEMPLATE_STRING_IF_INVALID which happens with the with block.
            value = filter.resolve(context, ignore_failures=True)
            if value is not None:
                break

        context[self.var_name] = value
        return ''

    @classmethod
    def parse(cls, parser, token):
        """
        Parse the node: {% getfirstof val1 val2 as val3 %}
        parser: a Parser class.
        token: a Token class.
        """
        bits = token.contents.split()  # splits on whitespace
        if len(bits) < 5:
            raise TemplateSyntaxError("'{0}' tag takes at least 4 arguments".format(bits[0]))
        if bits[-2] != 'as':
            raise TemplateSyntaxError("Expected syntax: {{% {0} val1 val2 as val %}}".format(bits[0]))

        choices = bits[1:-2]
        var_name = bits[-1]
        filters = [parser.compile_filter(bit) for bit in choices]
        return cls(filters, var_name)

@register.tag
def getfirstof(parser, token):
    return GetFirstOfNode.parse(parser, token)
