from django.core.exceptions import ImproperlyConfigured

VERSION = (0, 1, 0)
from fluent_contents.plugins.markup import appsettings

dependencies = {
    'restructuredtext': 'docutils',
    'markdown': 'markdown',
    'textile': 'textile',
    'creole': 'django_markup',
}


# Do some version checking
for language in appsettings.FLUENT_MARKUP_LANGUAGES:
    backendapp = dependencies.get(language)
    if backendapp:
        try:
            __import__(backendapp)
        except ImportError as e:
            raise ImportError("The '{0}' package is required to use the '{1}' language for the '{2}' plugin.".format(backendapp, language, 'markup'))


# Second round, check if language is supported.
from fluent_contents.plugins.markup import backend
for language in appsettings.FLUENT_MARKUP_LANGUAGES:
    if language not in backend.SUPPORTED_LANGUAGES:
        raise ImproperlyConfigured("markup filter does not exist: %s. Valid options are: %s" % (
            language, ', '.join(list(backend.SUPPORTED_LANGUAGES.keys()))
        ))
