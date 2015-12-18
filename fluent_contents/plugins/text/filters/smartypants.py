from __future__ import absolute_import
from django.core.exceptions import ImproperlyConfigured

try:
    from smartypants import smartypants
except ImportError:
    raise ImproperlyConfigured("Install 'smartypants' to use the smartypants filter")


def smartypants_filter(textitem, html):
    """
    Apply smartypants to the text.
    """
    return smartypants(html)
