"""
Markup plugin, rendering human readable formatted text to HTML.

This plugin supports several markup languages:

  reStructuredText: Used for Python documentation.
  Markdown: Used for GitHub and Stackoverflow comments (both have a dialect/extended version)
  Textile: A extensive markup format, also used in Redmine and partially in Basecamp.

"""

from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from fluent_contents.extensions import ContentPlugin, plugin_pool
from fluent_contents.plugins.markup.models import MarkupItem, MarkupItemForm, LANGUAGE_MODEL_CLASSES
from fluent_contents.plugins.markup import backend, appsettings


class MarkupPluginBase(ContentPlugin):
    """
    Base plugin for markup item models.
    The actual plugins are dynamically created.
    """
    model = MarkupItem
    category = _('Markup')
    form = MarkupItemForm
    admin_form_template = ContentPlugin.ADMIN_TEMPLATE_WITHOUT_LABELS
    search_output = True

    class Media:
        css = {'screen': ('fluent_contents/plugins/markup/markup_admin.css',)}

    def render(self, request, instance, **kwargs):
        try:
            html = backend.render_text(instance.text, instance.language)
        except Exception as e:
            html = self.render_error(e)

        # Included in a DIV, so the next item will be displayed below.
        return mark_safe('<div class="markup">' + html + '</div>\n')


def _create_markup_plugin(language, model):
    """
    Create a new MarkupPlugin class that represents the plugin type.
    """
    form = type("{0}MarkupItemForm".format(language.capitalize()), (MarkupItemForm,), {
        'default_language': language,
    })

    classname = "{0}MarkupPlugin".format(language.capitalize())
    PluginClass = type(classname, (MarkupPluginBase,), {
        'model': model,
        'form': form,
    })

    return PluginClass


# Dynamically create plugins for every language type.
# Allows adding them separately in the admin, while using the same database table.
for language, model in LANGUAGE_MODEL_CLASSES.items():
    if language not in appsettings.FLUENT_MARKUP_LANGUAGES:
        continue

    #globals()[classname] = PluginClass
    plugin_pool.register(_create_markup_plugin(language, model))
