"""
Settings for the markup part.
"""
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


COMMENTS_APP = getattr(settings, 'COMMENTS_APP', 'comments')
FLUENT_COMMENTSAREA_THREADEDCOMMENTS = 'threadedcomments' in settings.INSTALLED_APPS


# Test threadedcomments support
if FLUENT_COMMENTSAREA_THREADEDCOMMENTS:
    try:
        from threadedcomments.templatetags import threadedcomments_tags
    except ImportError:
        raise ImportError("The 'threadedcomments' package is too old to use for the 'commentsarea' plugin.")

    # Avoid getting an error that the Form misses a parent parameter.
    # The threadedcomments module needs to separate COMMENTS_APP setting.
    if not COMMENTS_APP or COMMENTS_APP == 'comments':
        raise ImproperlyConfigured("To use 'threadedcomments', specify the COMMENTS_APP as well")
