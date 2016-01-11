"""
Overview of all settings which can be customized.
"""
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from fluent_utils.load import import_class
from parler import appsettings as parler_appsettings

# By default, output is cached.
# Even for development, so the caching behavior are as realistically as possible.
# (though it will check whether the template file mtime changed in DEBUG mode)
FLUENT_CONTENTS_CACHE_OUTPUT = getattr(settings, 'FLUENT_CONTENTS_CACHE_OUTPUT', True)

# Cache the full output of placeholders.
# Not enabled in development by default, because that would annoy every ContentItem template change.
# Hence, this will not automatically toggle on in production, so configuration stays explicit.
FLUENT_CONTENTS_CACHE_PLACEHOLDER_OUTPUT = getattr(settings, 'FLUENT_CONTENTS_CACHE_PLACEHOLDER_OUTPUT', False)

FLUENT_CONTENTS_PLACEHOLDER_CONFIG = getattr(settings, 'FLUENT_CONTENTS_PLACEHOLDER_CONFIG', {})

# Note: the default language setting is used during the migrations
FLUENT_DEFAULT_LANGUAGE_CODE = getattr(settings, 'FLUENT_DEFAULT_LANGUAGE_CODE', parler_appsettings.PARLER_DEFAULT_LANGUAGE_CODE)
FLUENT_CONTENTS_DEFAULT_LANGUAGE_CODE = getattr(settings, 'FLUENT_CONTENTS_DEFAULT_LANGUAGE_CODE', FLUENT_DEFAULT_LANGUAGE_CODE)

# Allow to disable multisite support.
# Only used by sharedcontent plugin for now.
FLUENT_CONTENTS_FILTER_SITE_ID = getattr(settings, "FLUENT_CONTENTS_FILTER_SITE_ID", True)

# Settings for all PluginHtmlFields:
FLUENT_TEXT_CLEAN_HTML = getattr(settings, "FLUENT_TEXT_CLEAN_HTML", False)
FLUENT_TEXT_SANITIZE_HTML = getattr(settings, "FLUENT_TEXT_SANITIZE_HTML", False)

FLUENT_TEXT_PRE_FILTERS = getattr(settings, "FLUENT_TEXT_PRE_FILTERS", ())
FLUENT_TEXT_POST_FILTERS = getattr(settings, "FLUENT_TEXT_POST_FILTERS", ())


def _load_callables(setting_name, setting_value):
    funcs = []
    for import_path in setting_value:
        # TODO: replace with import_symbol() or import_func()
        func = import_class(import_path, setting_name)
        if not callable(func):
            raise ImproperlyConfigured("{0} element '{1}' is not callable!".format(setting_name, import_path))
        funcs.append(func)
    return funcs


PRE_FILTER_FUNCTIONS = _load_callables('FLUENT_TEXT_PRE_FILTERS', FLUENT_TEXT_PRE_FILTERS)
POST_FILTER_FUNCTIONS = _load_callables('FLUENT_TEXT_POST_FILTERS', FLUENT_TEXT_POST_FILTERS)

if FLUENT_TEXT_CLEAN_HTML or FLUENT_TEXT_SANITIZE_HTML:
    try:
        import django_wysiwyg
    except ImportError:
        raise ImproperlyConfigured(
            "The 'FLUENT_TEXT_CLEAN_HTML' and 'FLUENT_TEXT_SANITIZE_HTML' settings require django-wysiwyg to be installed."
        )
