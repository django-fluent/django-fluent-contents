"""
A proxy to automatically switch to the right comments app that is available.
"""
import warnings

from django.template import Library
from django.utils.safestring import mark_safe

from fluent_contents.plugins.commentsarea import appsettings
from fluent_utils.django_compat import is_installed


if is_installed('threadedcomments') and appsettings.FLUENT_COMMENTSAREA_THREADEDCOMMENTS:
    from threadedcomments.templatetags.threadedcomments_tags import register
elif is_installed('django.contrib.comments'):
    from django.contrib.comments.templatetags.comments import register
elif is_installed('django_comments'):
    from django_comments.templatetags.comments import register
else:
    register = Library()

    @register.simple_tag
    def render_comment_list(for_, object):
        warnings.warn(
            "Can't render comments list: no comment app installed!\n"
            "Make sure either 'django.contrib.comments' or 'django_comments' is in INSTALLED_APPS"
        )
        return mark_safe("<!-- Can't render comments list: no comment plugin installed! -->")

    @register.simple_tag
    def render_comment_form(for_, object):
        warnings.warn(
            "Can't render comments form: no comment app installed!\n"
            "Make sure either 'django.contrib.comments' or 'django_comments' is in INSTALLED_APPS"
        )
        return mark_safe("<!-- no comment plugin installed! -->")
