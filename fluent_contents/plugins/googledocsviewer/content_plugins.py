"""
Google apps widgets for your site.
"""
from django.utils.html import escape
from django.utils.http import urlquote
from django.utils.safestring import mark_safe
from fluent_contents.extensions import ContentPlugin, plugin_pool
from fluent_contents.plugins.googledocsviewer.models import GoogleDocsViewerItem


@plugin_pool.register
class GoogleDocsViewerPlugin(ContentPlugin):
    """
    Plugin to add a Google Docs viewer to the page.
    This can be used to display a PDF file inline.

    Note then when using the Google Docs viewer on your site,
    Google assumes you agree with the Terms of Service,
    see: https://docs.google.com/viewer/TOS
    """
    model = GoogleDocsViewerItem
    category = ContentPlugin.MEDIA

    def render(self, request, instance, **kwargs):
        url = 'http://docs.google.com/viewer?url={url}&embedded=true'.format(url=urlquote(instance.url, ''))
        return mark_safe(u'<iframe class="googledocsviewer" src="{src}" width="{width}" height="{height}"></iframe>'.format(
            src=escape(url),
            width=instance.width,
            height=instance.height
        ))
