import django
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

VERSION = (0, 1)

if django.VERSION < (1, 7):
    # TODO: this needs to be ported to system checks
    # providing these checks at import time breaks Django 1.7

    backendapp = 'disqus'

    # Do some settings checks.
    if backendapp not in settings.INSTALLED_APPS:
        raise ImproperlyConfigured("The '{0}' application is required to use the '{1}' plugin.".format(backendapp, 'disqusarea'))

    try:
        import disqus
    except ImportError:
        raise ImproperlyConfigured("The 'django-disqus' package is required to use the 'disqusarea' plugin.")

    for varname in ('DISQUS_API_KEY', 'DISQUS_WEBSITE_SHORTNAME'):
        if not getattr(settings, varname, None):
            raise ImproperlyConfigured("The '{0}' setting is required to use the '{1}' plugin.".format(varname, 'disqusarea'))
