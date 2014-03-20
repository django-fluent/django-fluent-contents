"""
Overview of all settings which can be customized.
"""
from django.conf import settings
from parler import appsettings as parler_appsettings


FLUENT_CONTENTS_CACHE_OUTPUT = getattr(settings, 'FLUENT_CONTENTS_CACHE_OUTPUT', True)

FLUENT_CONTENTS_PLACEHOLDER_CONFIG = getattr(settings, 'FLUENT_CONTENTS_PLACEHOLDER_CONFIG', {})

# Note: the default language setting is used during the migrations
FLUENT_DEFAULT_LANGUAGE_CODE = getattr(settings, 'FLUENT_DEFAULT_LANGUAGE_CODE', parler_appsettings.PARLER_DEFAULT_LANGUAGE_CODE)
FLUENT_CONTENTS_DEFAULT_LANGUAGE_CODE = getattr(settings, 'FLUENT_CONTENTS_DEFAULT_LANGUAGE_CODE', FLUENT_DEFAULT_LANGUAGE_CODE)

# Allow to disable multisite support.
# Only used by sharedcontent plugin for now.
FLUENT_CONTENTS_FILTER_SITE_ID = getattr(settings, "FLUENT_CONTENTS_FILTER_SITE_ID", True)
