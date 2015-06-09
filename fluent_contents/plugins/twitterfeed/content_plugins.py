from django.utils.translation import ugettext_lazy as _
from fluent_contents.extensions import ContentPlugin, plugin_pool
from fluent_contents.plugins.twitterfeed.models import TwitterRecentEntriesItem, TwitterSearchItem


class BaseTwitterPlugin(ContentPlugin):
    category = _('Media')


@plugin_pool.register
class TwitterRecentEntriesPlugin(BaseTwitterPlugin):
    """
    The plugin to display recent twitter entries of a user.
    """
    model = TwitterRecentEntriesItem
    render_template = "plugins/twitterfeed/recent_entries.html"


@plugin_pool.register
class TwitterSearchPlugin(BaseTwitterPlugin):
    """
    The plugin to display recent twitter entries of a user.
    """
    model = TwitterSearchItem
    render_template = "plugins/twitterfeed/search.html"
