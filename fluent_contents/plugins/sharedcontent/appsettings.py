"""
Settings for the text item.
"""
from django.conf import settings

# Allow the "cross site" feature in shared content:
FLUENT_SHARED_CONTENT_ENABLE_CROSS_SITE = getattr(settings, "FLUENT_SHARED_CONTENT_ENABLE_CROSS_SITE", True)
