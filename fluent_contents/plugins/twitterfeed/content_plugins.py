from fluent_contents.extensions import ContentPlugin, plugin_pool
from fluent_contents.plugins.twitterfeed.models import TwitterRecentEntriesItem, TwitterSearchItem


class BaseTwitterPlugin(ContentPlugin):
    category = ContentPlugin.MEDIA


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
