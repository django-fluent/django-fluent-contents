"""
Definition of the plugin.
"""
from django.utils.safestring import mark_safe
from fluent_contents.extensions import ContentPlugin, plugin_pool
from fluent_contents.plugins.text.models import TextItem


@plugin_pool.register
class TextPlugin(ContentPlugin):
    model = TextItem
    admin_init_template = "admin/fluent_contents/plugins/text/admin_init.html"  # TODO: remove the need for this.
    admin_form_template = ContentPlugin.ADMIN_TEMPLATE_WITHOUT_LABELS

    def render(self, request, instance, **kwargs):
        # Included in a DIV, so the next item will be displayed below.
        return mark_safe('<div class="text">' + instance.text + '</div>\n')
