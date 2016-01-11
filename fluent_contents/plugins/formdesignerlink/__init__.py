import django
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

VERSION = (0, 1)

if django.VERSION < (1, 7):
    # TODO: this needs to be ported to system checks
    # providing these checks at import time breaks Django 1.7

    backendapp = 'form_designer'

    # Do some settings checks.
    if backendapp not in settings.INSTALLED_APPS:
        raise ImproperlyConfigured("The '{0}' application is required to use the '{1}' plugin.".format(backendapp, 'formdesignerlink'))

    try:
        import form_designer
    except ImportError as e:
        raise ImproperlyConfigured("The 'django-form-designer' package is required to use the 'formdesignerlink' plugin.")
