from django.utils.safestring import mark_safe
from fluent_contents.extensions import ContentPlugin, plugin_pool
from fluent_contents.plugins.rawhtml.models import RawHtmlItem


@plugin_pool.register
class RawHtmlPlugin(ContentPlugin):
    """
    Plugin for rendering raw HTML output.
    This can be used to insert embed codes in a webpage,
    for example for Google Docs, YouTube or SlideShare.
    """
    model = RawHtmlItem
    category = ContentPlugin.ADVANCED
    admin_form_template = ContentPlugin.ADMIN_TEMPLATE_WITHOUT_LABELS

    class Media:
        css = {'screen': ('fluent_contents/plugins/rawhtml/rawhtml_admin.css',)}

    def render(self, request, instance, **kwargs):
        return mark_safe(instance.html)
