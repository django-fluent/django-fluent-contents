"""
Plugin for rendering Gist snippets, hosted by Github.
"""
from django.utils.http import urlquote
from django.utils.safestring import mark_safe
from fluent_contents.extensions import ContentPlugin, plugin_pool
from fluent_contents.plugins.gist.models import GistItem


@plugin_pool.register
class GistPlugin(ContentPlugin):
    model = GistItem
    category = ContentPlugin.PROGRAMMING

    def render(self, request, instance, **kwargs):
        url = u'http://gist.github.com/{0}.js'.format(instance.gist_id)
        if instance.filename:
            url += u'?file={0}'.format(urlquote(instance.filename))

        return mark_safe(u'<script src="{0}"></script>'.format(url))
