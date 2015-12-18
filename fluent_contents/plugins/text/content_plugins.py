"""
Definition of the plugin.
"""
from django.utils.html import format_html
from fluent_contents.extensions import ContentPlugin, plugin_pool, ContentItemForm
from fluent_contents.plugins.text.models import TextItem


class TextItemForm(ContentItemForm):
    """
    Perform extra processing for the text item
    """

    def clean_text(self, html):
        """
        Perform the cleanup in the form, allowing to raise a ValidationError
        """
        return self.instance.apply_pre_filters(html)


@plugin_pool.register
class TextPlugin(ContentPlugin):
    """
    CMS plugin for WYSIWYG text items.
    """
    model = TextItem
    form = TextItemForm
    admin_init_template = "admin/fluent_contents/plugins/text/admin_init.html"  # TODO: remove the need for this.
    admin_form_template = ContentPlugin.ADMIN_TEMPLATE_WITHOUT_LABELS

    def render(self, request, instance, **kwargs):
        # Included in a DIV, so the next item will be displayed below.
        # The text_final is allowed to be None, to migrate old plugins.
        text = instance.text if instance.text_final is None else instance.text_final
        return format_html(u'<div class="text">{0}</div>\n', text)
