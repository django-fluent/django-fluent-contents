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
from fluent_utils.softdeps.any_urlfield import AnyUrlField
from fluent_utils.softdeps.any_imagefield import AnyFileField, AnyImageField

from fluent_contents import appsettings
from fluent_contents.forms.widgets import WysiwygWidget
from fluent_contents.utils.html import clean_html, sanitize_html


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

    Use this instead of the standard :class:`~django.db.models.URLField`.
    """


class PluginFileField(MigrationMixin, AnyFileField):
    """
    A file upload field for plugins.

    Use this instead of the standard :class:`~django.db.models.FileField`.
    """


class PluginImageField(MigrationMixin, AnyImageField):
    """
    An image upload field for plugins.

    Use this instead of the standard :class:`~django.db.models.ImageField`.
    """


class PluginHtmlField(MigrationMixin, models.TextField):
    """
    A HTML field for plugins.

    This field is replaced with a django-wysiwyg editor in the admin.
    """

    def __init__(self, *args, **kwargs):
        # This method override is primary included to improve the API documentation
        super(PluginHtmlField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'widget': WysiwygWidget}
        defaults.update(kwargs)

        return super(PluginHtmlField, self).formfield(**defaults)

    def to_python(self, html):
        # Make well-formed if requested
        if appsettings.FLUENT_TEXT_CLEAN_HTML:
            html = clean_html(html)

        # Remove unwanted tags if requested
        if appsettings.FLUENT_TEXT_SANITIZE_HTML:
            html = sanitize_html(html)

        return mark_safe(html)


# Tell the Django admin it shouldn't override the widget because it's a TextField
from django.contrib.admin import options
options.FORMFIELD_FOR_DBFIELD_DEFAULTS[PluginHtmlField] = {'widget': WysiwygWidget}
