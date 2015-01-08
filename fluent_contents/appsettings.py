"""
Overview of all settings which can be customized.
"""
from django.conf import settings
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
