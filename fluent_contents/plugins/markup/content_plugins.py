"""
Markup plugin, rendering human readable formatted text to HTML.

This plugin supports several markup languages:

  reStructuredText: Used for Python documentation.
  Markdown: Used for GitHub and Stackoverflow comments (both have a dialect/extended version)
  Textile: A extensive markup format, also used in Redmine and partially in Basecamp.

"""
from django.utils.translation import ugettext_lazy as _
from fluent_contents.extensions import ContentPlugin, plugin_pool
from fluent_contents.plugins.markup.models import MarkupItem, MarkupItemForm
from fluent_contents.plugins.markup import backend


class MarkupPlugin(ContentPlugin):
    model = MarkupItem
    category = _('Programming')
    admin_form = MarkupItemForm
    admin_form_template = ContentPlugin.ADMIN_TEMPLATE_WITHOUT_LABELS


    def render(self, instance, request, **kwargs):
        try:
            html = backend.render_text(instance.text, instance.language)
        except Exception, e:
            html = self.render_error(e)

        # Included in a DIV, so the next item will be displayed below.
        return '<div class="markup">' + html + '</div>\n'


plugin_pool.register(MarkupPlugin)
