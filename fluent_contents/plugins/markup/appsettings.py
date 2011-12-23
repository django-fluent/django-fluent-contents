"""
Settings for the markup item.
"""
from django.conf import settings

FLUENT_MARKUP_LANGUAGE = getattr(settings, "FLUENT_MARKUP_LANGUAGE", 'restructuredtext')
FLUENT_MARKUP_MARKDOWN_EXTRAS = getattr(settings, "FLUENT_MARKUP_MARKDOWN_EXTRAS", [])

# Experimental:
FLUENT_MARKUP_USE_DJANGO_MARKUP = getattr(settings, 'FLUENT_MARKUP_USE_DJANGO_MARKUP', False)
