from django.forms.widgets import Widget
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

class PlaceholderFieldWidget(Widget):
    """
    The widget to render a :class:`fluent_contents.models.PlaceholderField`.

    It outputs a ``<div>`` element which operates as placeholder content area.
    The client-side editor will use that area to display the admin interfaces of the :class:`fluent_contents.models.ContentItem` models.
    """

    class Media:
        js = (
            'fluent_contents/admin/cp_admin.js',
            'fluent_contents/admin/cp_data.js',
            'fluent_contents/admin/cp_plugins.js',
        )
        css = {
            'screen': (
                'fluent_contents/admin/cp_admin.css',
            ),
        }


    def __init__(self, attrs=None, slot=None, plugins=None):
        from fluent_contents import extensions   # Avoid circular reference because __init__.py imports subfolders too
        super(PlaceholderFieldWidget, self).__init__(attrs)
        self.slot = slot
        self.plugins = extensions.plugin_pool.get_plugins() if plugins is None else plugins


    def value_from_datadict(self, data, files, name):
        # This returns the field value from the form POST fields.
        # Currently returns a dummy value, so the PlaceholderFieldDescriptor() can detect it.
        return "-DUMMY-"


    def render(self, name, value, attrs=None):
        """
        Render the placeholder field.
        """
        context = {
            'cp_plugin_list': self.plugins,
            'placeholder_id': '',
            'placeholder_slot': self.slot,
        }
        return mark_safe(render_to_string('admin/fluent_contents/placeholderfield/widget.html', context))
