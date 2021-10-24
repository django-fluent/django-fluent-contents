"""
Definition of the plugin.
"""
from django.utils.safestring import mark_safe

from fluent_contents.extensions import ContentPlugin, plugin_pool
from fluent_contents.plugins.text.models import TextItem


@plugin_pool.register
class TextPlugin(ContentPlugin):
    """
    CMS plugin for WYSIWYG text items.
    """

    model = TextItem
    # TODO: remove the need for admin_init_template.
    admin_init_template = "admin/fluent_contents/plugins/text/admin_init.html"
    admin_form_template = ContentPlugin.ADMIN_TEMPLATE_WITHOUT_LABELS
    search_output = True

    def render(self, request, instance, **kwargs):
        # Included in a DIV, so the next item will be displayed below.
        # The text_final is allowed to be None, to migrate old plugins.
        text = instance.text if instance.text_final is None else instance.text_final
        return mark_safe(f'<div class="text">{text}</div>\n')
