from django.utils.translation import ugettext_lazy as _
from fluent_contents.extensions import ContentPlugin, plugin_pool, TabularPluginInline
from .models import LinkListItem, Link


class LinkInline(TabularPluginInline):
    model = Link
    extra = 3


@plugin_pool.register
class LinkListPlugin(ContentPlugin):
    """
    Plugin for rendering a list of links.
    """
    model = LinkListItem
    category = _('Media')
    render_template = "fluent_contents/plugins/linklist/default.html"
    inlines = (LinkInline,)
