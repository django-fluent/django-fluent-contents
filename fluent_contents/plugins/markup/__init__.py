from django.core.exceptions import ImproperlyConfigured

VERSION = (0, 1, 0)
from fluent_contents.plugins.markup import appsettings

dependencies = {
    'restructuredtext': 'docutils',
    'markdown': 'markdown',
    'textile': 'textile',
    'creole': '',
}


# Do some version checking
backendapp = dependencies.get(appsettings.FLUENT_MARKUP_LANGUAGE)
try:
    if backendapp:
        __import__(backendapp)
except ImportError, e:
    raise ImportError("The '{0}' package is required to use the '{1}' language for the '{2}' plugin.".format(backendapp, appsettings.FLUENT_MARKUP_LANGUAGE, 'markup'))

from fluent_contents.plugins.markup import backend
if appsettings.FLUENT_MARKUP_LANGUAGE not in backend.SUPPORTED_LANGUAGES:
    raise ImproperlyConfigured("markup filter does not exist: %s. Valid options are: %s" % (
        appsettings.FLUENT_MARKUP_LANGUAGE, ', '.join(backend.SUPPORTED_LANGUAGES.keys())
    ))
