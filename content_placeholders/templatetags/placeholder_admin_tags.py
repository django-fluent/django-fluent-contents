from django.template import Library
from content_placeholders.admin.contentitems import ContentItemInline

register = Library()

@register.filter
def only_content_item_inlines(inlines):
    return [i for i in inlines if isinstance(i, ContentItemInline)]


@register.filter
def only_content_item_formsets(formsets):
    return [f for f in formsets if isinstance(f.opts, ContentItemInline)]


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
        title = plugin.category or ""
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
