"""
Settings for the markup item.
"""
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

_SUPPORTED_LANGUAGES = (
    'restructuredtext',
    'markdown',
    'textile',
)

FLUENT_MARKUP_LANGUAGES = getattr(settings, "FLUENT_MARKUP_LANGUAGES", ['restructuredtext', 'markdown', 'textile'])
FLUENT_MARKUP_MARKDOWN_EXTRAS = getattr(settings, "FLUENT_MARKUP_MARKDOWN_EXTRAS", [])

# Experimental:
FLUENT_MARKUP_USE_DJANGO_MARKUP = getattr(settings, 'FLUENT_MARKUP_USE_DJANGO_MARKUP', False)

dependencies = {
    'restructuredtext': 'docutils',
    'markdown': 'markdown',
    'textile': 'textile',
    'creole': 'django_markup',
}


# Do some version checking
for language in FLUENT_MARKUP_LANGUAGES:
    backendapp = dependencies.get(language)
    if backendapp:
        try:
            __import__(backendapp)
        except ImportError as e:
            raise ImproperlyConfigured("The '{0}' package is required to use the '{1}' language for the '{2}' plugin.".format(backendapp, language, 'markup'))


# Second round, check if language is supported.
for language in FLUENT_MARKUP_LANGUAGES:
    if language not in _SUPPORTED_LANGUAGES:
        raise ImproperlyConfigured("markup filter does not exist: %s. Valid options are: %s" % (
            language, ', '.join(sorted(_SUPPORTED_LANGUAGES))
        ))
