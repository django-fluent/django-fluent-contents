"""
Plugin for rendering Gist snippets, hosted by Github.
"""
from urllib.parse import quote

from django.utils.safestring import mark_safe

from fluent_contents.extensions import ContentPlugin, plugin_pool
from fluent_contents.plugins.gist.models import GistItem


@plugin_pool.register
class GistPlugin(ContentPlugin):
    model = GistItem
    category = ContentPlugin.PROGRAMMING

    def render(self, request, instance, **kwargs):
        url = f"http://gist.github.com/{instance.gist_id}.js"
        if instance.filename:
            url += f"?file={urlquote(instance.filename)}"

        return mark_safe(f'<script src="{url}"></script>')
