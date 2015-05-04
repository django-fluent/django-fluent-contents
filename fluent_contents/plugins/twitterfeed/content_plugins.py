from fluent_contents.extensions import ContentPlugin, plugin_pool
from fluent_contents.plugins.twitterfeed import appsettings
from fluent_contents.plugins.twitterfeed.models import TwitterRecentEntriesItem, TwitterSearchItem


class BaseTwitterPlugin(ContentPlugin):
    category = ContentPlugin.MEDIA

    def get_context(self, request, instance, **kwargs):
        context = super(BaseTwitterPlugin, self).get_context(request, instance, **kwargs)
        context.update({
            'AVATAR_SIZE': int(appsettings.FLUENT_TWITTERFEED_AVATAR_SIZE),
            'REFRESH_INTERVAL': int(appsettings.FLUENT_TWITTERFEED_REFRESH_INTERVAL),
            'TEXT_TEMPLATE': appsettings.FLUENT_TWITTERFEED_TEXT_TEMPLATE,
        })
        return context


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
