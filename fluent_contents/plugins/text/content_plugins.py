"""
Definition of the plugin.
"""
from fluent_contents.extensions import ContentPlugin, plugin_pool
from fluent_contents.plugins.text.models import TextItem


class TextPlugin(ContentPlugin):
    model = TextItem
    admin_form_template = ContentPlugin.ADMIN_TEMPLATE_WITHOUT_LABELS

    class Media:
        js = ('fluent_contents/plugins/text/text_admin.js',)
        css = {'screen': ('fluent_contents/plugins/text/text_admin.css',)}

    def render(self, instance, request, **kwargs):
        # Included in a DIV, so the next item will be displayed below.
        return '<div class="text">' + instance.text + '</div>\n'


plugin_pool.register(TextPlugin)
