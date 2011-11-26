from urlparse import urljoin
from django.forms.widgets import Widget
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from content_placeholders.extensions import plugin_pool
from content_placeholders.models.db import Placeholder

class PluginEditor(Widget):
    class Media:
        js = (
            'content_placeholders/admin/cp_admin.js',
            'content_placeholders/admin/cp_data.js',
            'content_placeholders/admin/cp_plugins.js',
        )
        css = {
            'screen': (
                'content_placeholders/admin/cp_admin.css',
            ),
        }

    def render(self, name, value, attrs=None):
        return mark_safe(render_to_string('admin/content_placeholders/placeholderfield/widget.html', {}))
        context = {
            'plugin_list': self.attrs['list'],
            'installed_plugins': self.attrs['installed'],
            'copy_languages': self.attrs['copy_languages'],
            'language': self.attrs['language'],
            'show_copy': self.attrs['show_copy'],
            'placeholder': self.attrs['placeholder'],
        }
        return mark_safe(render_to_string('admin/content_placeholders/placeholderfield/widget.html', context))


class PlaceholderPluginEditor(PluginEditor):
    def x_render(self, name, value, attrs=None):
        try:
            ph = Placeholder.objects.get(pk=value)
        except Placeholder.DoesNotExist:
            ph = None
            context = {'add':True}
        if ph:
            plugin_list = ph.cmsplugin_set.filter(parent=None).order_by('position')
            context = {
                'plugin_list': plugin_list,
                'installed_plugins': plugin_pool.get_all_plugins(ph.slot),
                'urloverride': True,
                'placeholder': ph,
            }
        return mark_safe(render_to_string('admin/cms/page/widgets/placeholder_editor.html', context, RequestContext(self.request)))
