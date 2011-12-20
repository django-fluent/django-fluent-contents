"""
Plugin for rendering Gist snippets, hosted by Github.
"""
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
from fluent_contents.extensions import ContentPlugin, plugin_pool
from fluent_contents.plugins.gist.models import GistItem


class GistPlugin(ContentPlugin):
    model = GistItem
    category = _('Programming')


    def render(self, instance, request, **kwargs):
        url = u'http://gist.github.com/{0}.js'.format(instance.gist_id)
        if instance.filename:
            url += u'?file={0}'.format(urlquote(instance.filename))

        return u'<script src="{0}"></script>'.format(url)


plugin_pool.register(GistPlugin)
