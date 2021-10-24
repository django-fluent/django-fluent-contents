from article.models import ArticleTextItem

from fluent_contents.extensions import ContentPlugin, plugin_pool


class ArticleTextPlugin(ContentPlugin):
    name = "Text item"
    category = "Content plugins"
    model = ArticleTextItem
    render_template = "article/plugins/text.html"


plugin_pool.register(ArticleTextPlugin)
