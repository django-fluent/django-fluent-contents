"""
Settings for the markup item.
"""
from django.conf import settings

# NOTE: The checks whether FLUENT_MARKUP_LANGUAGES contains valid values happens in __init__.py
FLUENT_MARKUP_LANGUAGES = getattr(settings, "FLUENT_MARKUP_LANGUAGES", ['restructuredtext', 'markdown', 'textile'])
FLUENT_MARKUP_MARKDOWN_EXTRAS = getattr(settings, "FLUENT_MARKUP_MARKDOWN_EXTRAS", [])

# Experimental:
FLUENT_MARKUP_USE_DJANGO_MARKUP = getattr(settings, 'FLUENT_MARKUP_USE_DJANGO_MARKUP', False)
