"""
Overview of all settings which can be customized.
"""
from django.conf import settings

FLUENT_CONTENTS_CACHE_OUTPUT = getattr(settings, 'FLUENT_CONTENTS_CACHE_OUTPUT', True)

FLUENT_CONTENTS_PLACEHOLDER_CONFIG = getattr(settings, 'FLUENT_CONTENTS_PLACEHOLDER_CONFIG', {})

# Note: the default language setting is used during the migrations
FLUENT_DEFAULT_LANGUAGE_CODE = getattr(settings, 'FLUENT_DEFAULT_LANGUAGE_CODE', settings.LANGUAGE_CODE)
FLUENT_CONTENTS_DEFAULT_LANGUAGE_CODE = getattr(settings, 'FLUENT_CONTENTS_DEFAULT_LANGUAGE_CODE', FLUENT_DEFAULT_LANGUAGE_CODE)
