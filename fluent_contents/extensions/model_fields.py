"""
This is an internal module for the plugin system,
the API is exposed via __init__.py

This package contains model fields which are usable for extensions.
It has a soft coupling to the real apps that are being used,
which makes it easy to switch the complete plugin file/url/html fields
This avoids fixing the generic plugin to specific Django extensions or packages.
Each project can use their preferred file browser/image browser/URL selector for the entire site.

Using *django-any-urlfield* or *django-any-imagefield* is completely optional, yet highly recommended.
When those apps are installed, they are used by the plugins.
"""
from django.db import models
from django.utils.safestring import mark_safe
from fluent_contents.forms.widgets import WysiwygWidget
from fluent_utils.softdeps.any_urlfield import AnyUrlField
from fluent_utils.softdeps.any_imagefield import AnyFileField, AnyImageField

_this_module_name = __name__
def _get_path(cls):
    module = cls.__module__
    # Hide ".model_fields" unless the field is overwritten.
    if module == _this_module_name:
        module = 'fluent_contents.extensions'
    return "{0}.{1}".format(module, cls.__name__)


class MigrationMixin(object):
    def south_field_triple(self):
        # Undo the softdep feature
        # Show as Plugin..Field in the migrations.
        from south.modelsinspector import introspector
        path = _get_path(self.__class__)
        args, kwargs = introspector(self)
        return (path, args, kwargs)

    def deconstruct(self):
        # Don't masquerade as optional field like fluent-utils does,
        # Show as Plugin..Field in the migrations.
        name, path, args, kwargs = super(MigrationMixin, self).deconstruct()
        path = _get_path(self.__class__)
        return name, path, args, kwargs


class PluginUrlField(MigrationMixin, AnyUrlField):
    """
    An URL field for plugins.
    """


class PluginFileField(MigrationMixin, AnyFileField):
    """
    A file upload field for plugins.
    """


class PluginImageField(MigrationMixin, AnyImageField):
    """
    A image upload field for plugins.
    """


class PluginHtmlField(MigrationMixin, models.TextField):
    """
    A large string field for HTML content; it's replaced with django-wysiwyg in the admin.
    """
    def __init__(self, *args, **kwargs):
        # This method override is primary included to improve the API documentation
        super(PluginHtmlField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'widget': WysiwygWidget}
        defaults.update(kwargs)

        return super(PluginHtmlField, self).formfield(**defaults)

    def to_python(self, value):
        return mark_safe(value)


# Tell the Django admin it shouldn't override the widget because it's a TextField
from django.contrib.admin import options
options.FORMFIELD_FOR_DBFIELD_DEFAULTS[PluginHtmlField] = {'widget': WysiwygWidget}
