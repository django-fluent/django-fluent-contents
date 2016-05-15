"""
Comments area plugin.

This plugin package is not called "comments" as that conflicts
with the `django.contrib.comments` appname. Hence, "commentsarea" it is.

The plugin displays the form and messagelist that ``django.contrib.comments`` renders.
Hence, it depends on a properly configured contrib module.
The least you need to do, is:

  * providing a ``comments/base.html`` template.
   * include a ``title`` block that is displayed in the ``<head>`` of the base template.
   * include a ``content`` block that is displayed in the ``<body>`` of the base template.
  * provide a ``comments/posted.html`` template for the success page.
   * It could contains links to the blog page.
   * It could redirect automatically back to the blog in a few seconds.
"""
from django.conf import settings

from fluent_contents.extensions import ContentPlugin, plugin_pool
from fluent_contents.plugins.commentsarea.models import CommentsAreaItem
from . import appsettings


@plugin_pool.register
class CommentsAreaPlugin(ContentPlugin):
    model = CommentsAreaItem
    category = ContentPlugin.INTERACTIVITY
    render_template = "fluent_contents/plugins/commentsarea/commentsarea.html"

    if 'fluent_comments' in settings.INSTALLED_APPS and appsettings.FLUENT_COMMENTSAREA_INCLUDE_STATIC_FILES:
        class FrontendMedia:
            css = {
                'screen': ('fluent_comments/css/ajaxcomments.css',),
            }
            js = (
                'fluent_comments/js/ajaxcomments.js',
            )
