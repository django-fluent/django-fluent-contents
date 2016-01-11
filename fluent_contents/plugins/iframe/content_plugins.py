"""
Plugin to add an ``<iframe>`` to the page.
"""
from django.utils.html import escape
from django.utils.safestring import mark_safe
from fluent_contents.extensions import ContentPlugin, plugin_pool
from fluent_contents.plugins.iframe.models import IframeItem


@plugin_pool.register
class IframePlugin(ContentPlugin):
    model = IframeItem
    category = ContentPlugin.ADVANCED

    def render(self, request, instance, **kwargs):
        return mark_safe(u'<iframe class="iframe" src="{src}" width="{width}" height="{height}"></iframe>'.format(
            src=escape(instance.src),
            width=instance.width,
            height=instance.height
        ))
