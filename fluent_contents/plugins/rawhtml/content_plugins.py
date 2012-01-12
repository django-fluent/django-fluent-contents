from django.utils.translation import ugettext_lazy as _
from fluent_contents.extensions import ContentPlugin, plugin_pool
from fluent_contents.plugins.rawhtml.models import RawHtmlItem


class RawHtmlPlugin(ContentPlugin):
    """
    Plugin for rendering raw HTML output.
    This can be used to insert embed codes in a webpage,
    for example for Google Docs, YouTube or SlideShare.
    """
    model = RawHtmlItem
    category = _('Advanced')
    admin_form_template = ContentPlugin.ADMIN_TEMPLATE_WITHOUT_LABELS

    class Media:
        css = {'screen': ('fluent_contents/plugins/rawhtml/rawhtml_admin.css',)}


    def render(self, request, instance, **kwargs):
        return instance.html


plugin_pool.register(RawHtmlPlugin)
