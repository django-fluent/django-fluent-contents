"""
This is an internal module for the plugin system,
the API is exposed via __init__.py

This package contains model fields which are usable for extensions.
"""
from django.conf import settings
from django.db import models


# Keep the apps optional, however, it's highly recommended to use them.
# This avoids fixing the generic plugin to specific extensions.
# Each project can use their preferred file browser/image browser/URL selector for the entire site.
if 'any_urlfield' in settings.INSTALLED_APPS:
    from any_urlfield.models import AnyUrlField
    PluginUrlField = AnyUrlField
else:
    PluginUrlField = models.URLField


if 'any_imagefield' in settings.INSTALLED_APPS:
    from any_imagefield.models import AnyFileField, AnyImageField
    PluginFileField = AnyFileField
    PluginImageField = AnyImageField
else:
    PluginFileField = models.FileField
    PluginImageField = models.ImageField
