"""
A proxy to automatically switch to the ``threadedcomments`` template tags if they are available.
"""
from django.contrib.comments.templatetags import comments
from django import template
from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string
from fluent_contents.plugins.commentsarea import appsettings

register = template.Library()


if appsettings.FLUENT_COMMENTSAREA_THREADEDCOMMENTS:
    # Support threadedcomments
    from threadedcomments.templatetags import threadedcomments_tags  # If this import fails, the module version is too old.
    register.filters.update(threadedcomments_tags.register.filters)
    register.tags.update(threadedcomments_tags.register.tags)

    # https://github.com/HonzaKral/django-threadedcomments didn't have a 'render_comment_list' tag for a long time.
    if 'render_comment_list' not in register.tags:
        raise ImproperlyConfigured(
            "The current version of django-threadedcomments is not up-to-date.\n"
            "Please install django-threadedcomments >= 0.9")
else:
    # Standard comments
    register.filters.update(comments.register.filters)
    register.tags.update(comments.register.tags)
