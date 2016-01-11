from future.builtins import str
from django.template import Library, Node
from django.template.base import TemplateSyntaxError
from fluent_contents.admin.contentitems import BaseContentItemInline
from tag_parser import template_tag, parse_as_var, parse_token_kwargs

register = Library()


@register.filter
def only_content_item_inlines(inlines):
    return [i for i in inlines if isinstance(i, BaseContentItemInline)]


@register.filter
def only_content_item_formsets(formsets):
    return [f for f in formsets if isinstance(f.opts, BaseContentItemInline)]


@register.filter
def has_no_visible_fields(inline_admin_form):
    # fieldset = admin Fieldset object.

    for name, options in inline_admin_form.fieldsets:
        for name_slot in options.get('fields', ()):
            # Lines can include (field, field)
            if not isinstance(name_slot, (list, tuple)):
                name_slot = [name_slot]
            for name in name_slot:
                if not inline_admin_form.form.fields[name].widget.is_hidden:
                    return False

    return True


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
        title = str(plugin.category or u"")  # enforce resolving ugettext_lazy proxies.
        if title not in categories:
            categories[title] = []
        categories[title].append(plugin)

    return categories


@register.filter
def plugin_categories_to_list(plugin_categories):
    if not plugin_categories:
        return []
    categories_list = list(plugin_categories.items())
    categories_list.sort(key=lambda item: item[0])  # sort category names
    return categories_list


@register.filter
def plugin_categories_to_choices(categories):
    """
    Return a tuple of plugin model choices, suitable for a select field.
    Each tuple is a ("TypeName", "Title") value.
    """
    choices = []
    for category, items in categories.items():
        if items:
            plugin_tuples = tuple((plugin.type_name, plugin.verbose_name) for plugin in items)
            if category:
                choices.append((category, plugin_tuples))
            else:
                choices += plugin_tuples

    choices.sort(key=lambda item: item[0])
    return choices


@template_tag(register, 'getfirstof')
class GetFirstOfNode(Node):

    def __init__(self, filters, var_name):
        self.filters = filters    # list of FilterExpression nodes.
        self.var_name = var_name

    def render(self, context):
        value = None
        for filterexpr in self.filters:
            # The ignore_failures argument is the most important, otherwise
            # the value is converted to the TEMPLATE_STRING_IF_INVALID which happens with the with block.
            value = filterexpr.resolve(context, ignore_failures=True)
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
        bits, var_name = parse_as_var(parser, token)
        tag_name, choices, _ = parse_token_kwargs(parser, bits, allowed_kwargs=())

        if var_name is None:
            raise TemplateSyntaxError("Expected syntax: {{% {0} val1 val2 as val %}}".format(tag_name))

        return cls(choices, var_name)
