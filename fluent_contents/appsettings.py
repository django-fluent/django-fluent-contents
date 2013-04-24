"""
Overview of all settings which can be customized.
"""
from django.conf import settings

FLUENT_CONTENTS_CACHE_OUTPUT = getattr(settings, 'FLUENT_CONTENTS_CACHE_OUTPUT', True)

FLUENT_CONTENTS_PLACEHOLDER_CONFIG = getattr(settings, 'FLUENT_CONTENTS_PLACEHOLDER_CONFIG', {})
