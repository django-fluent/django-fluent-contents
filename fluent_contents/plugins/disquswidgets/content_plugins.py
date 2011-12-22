from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from fluent_contents.extensions import ContentPlugin, plugin_pool
from fluent_contents.plugins.disquswidgets.models import DisqusCommentsAreaItem


class DisqusCommentsPlugin(ContentPlugin):
    model = DisqusCommentsAreaItem
    category = _('Interactivity')
    render_template = "fluent_contents/plugins/disquswidgets/comments.html"


    def get_context(self, instance, request, **kwargs):
        return {
            'instance': instance,
            'DISQUS_WEBSITE_SHORTNAME': settings.DISQUS_WEBSITE_SHORTNAME,
            'DEBUG': settings.DEBUG,
        }


plugin_pool.register(DisqusCommentsPlugin)
