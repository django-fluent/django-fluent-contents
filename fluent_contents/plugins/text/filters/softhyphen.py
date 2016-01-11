from __future__ import absolute_import
from django.core.exceptions import ImproperlyConfigured

try:
    from softhyphen.html import hyphenate
except ImportError:
    raise ImproperlyConfigured("Install 'django-softhyphen' to use the softhyphen filter")


def softhyphen_filter(textitem, html):
    """
    Apply soft hyphenation to the text, which inserts ``&shy;`` markers.
    """
    language = textitem.language_code

    # Make sure the Django language code gets converted to what django-softhypen 1.0.2 needs.
    if language == 'en':
        language = 'en-us'
    elif '-' not in language:
        language = "{0}-{0}".format(language)

    return hyphenate(html, language=language)
