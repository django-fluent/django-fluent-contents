from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

VERSION = (0, 1)

backendapp = 'form_designer'

# Do some settings checks.
if backendapp not in settings.INSTALLED_APPS:
    raise ImproperlyConfigured("The '{0}' application is required to use the '{1}' plugin.".format(backendapp, 'formdesignerlink'))

try:
    import form_designer
except ImportError as e:
    raise ImportError("The 'django-form-designer' package is required to use the 'formdesignerlink' plugin.")
