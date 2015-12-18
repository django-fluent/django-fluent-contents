"""
Settings for the text item.
"""
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from fluent_utils.load import import_class

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
