from django.conf import settings
from django.contrib.admin.widgets import AdminTextareaWidget
from django.forms.utils import flatatt
from django.forms.widgets import Widget
from django.template.loader import render_to_string
from django.utils.encoding import smart_text
from django.utils.safestring import mark_safe
from django.utils.html import escape
from fluent_contents.models import get_parent_language_code
from fluent_contents.models.managers import get_parent_active_language_choices


class PlaceholderFieldWidget(Widget):
    """
    The widget to render a :class:`fluent_contents.models.PlaceholderField`.

    It outputs a ``<div>`` element which operates as placeholder content area.
    The client-side editor will use that area to display the admin interfaces of the :class:`fluent_contents.models.ContentItem` models.
    """

    class Media:
        js = (
            'admin/js/vendor/jquery/jquery{}.js'.format('' if settings.DEBUG else '.min'),
            'admin/js/jquery.init.js',
            'fluent_contents/admin/cp_admin.js',
            'fluent_contents/admin/cp_data.js',
            'fluent_contents/admin/cp_plugins.js',
        )
        css = {
            'screen': (
                'fluent_contents/admin/cp_admin.css',
            ),
        }

    def __init__(self, attrs=None, slot=None, parent_object=None, plugins=None):
        super(PlaceholderFieldWidget, self).__init__(attrs)
        self.slot = slot
        self._plugins = plugins
        self.parent_object = parent_object

    def value_from_datadict(self, data, files, name):
        # This returns the field value from the form POST fields.
        # Currently returns a dummy value, so the PlaceholderFieldDescriptor() can detect it.
        return "-DUMMY-"

    def render(self, name, value, attrs=None, renderer=None):
        """
        Render the placeholder field.
        """
        other_instance_languages = None
        if value and value != "-DUMMY-":
            if get_parent_language_code(self.parent_object):
                # Parent is a multilingual object, provide information
                # for the copy dialog.
                other_instance_languages = get_parent_active_language_choices(
                    self.parent_object, exclude_current=True)

        context = {
            'cp_plugin_list': list(self.plugins),
            'placeholder_id': '',
            'placeholder_slot': self.slot,
            'other_instance_languages': other_instance_languages,
        }
        return mark_safe(render_to_string('admin/fluent_contents/placeholderfield/widget.html', context))

    @property
    def plugins(self):
        """
        Get the set of plugins that this widget should display.
        """
        from fluent_contents import extensions   # Avoid circular reference because __init__.py imports subfolders too
        if self._plugins is None:
            return extensions.plugin_pool.get_plugins()
        else:
            return extensions.plugin_pool.get_plugins_by_name(*self._plugins)


class WysiwygWidget(AdminTextareaWidget):
    """
    WYSIWYG widget
    """

    def __init__(self, attrs=None):
        defaults = {'rows': 4}
        if attrs:
            defaults.update(attrs)
        super(WysiwygWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None, renderer=None):
        value = smart_text(value or u'')
        final_attrs = self.build_attrs(attrs)  # signature changed in Django 1.11
        final_attrs['name'] = name

        if 'class' in final_attrs:
            final_attrs['class'] += ' cp-wysiwyg-widget'
        else:
            final_attrs['class'] = 'cp-wysiwyg-widget'

        return mark_safe(u'<textarea{0}>{1}</textarea>'.format(flatatt(final_attrs), escape(value)))
