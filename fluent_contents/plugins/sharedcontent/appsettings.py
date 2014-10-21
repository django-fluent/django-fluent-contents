"""
Settings for the text item.
"""
from django.conf import settings
from fluent_contents import appsettings

# Reexport
FLUENT_CONTENTS_FILTER_SITE_ID = appsettings.FLUENT_CONTENTS_FILTER_SITE_ID


# Allow the "cross site" feature in shared content:
FLUENT_SHARED_CONTENT_ENABLE_CROSS_SITE = getattr(settings, "FLUENT_SHARED_CONTENT_ENABLE_CROSS_SITE", True)
