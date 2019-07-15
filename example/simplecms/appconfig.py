from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

SIMPLECMS_TEMPLATE_CHOICES = getattr(settings, "SIMPLECMS_TEMPLATE_CHOICES", ())
SIMPLECMS_DEFAULT_TEMPLATE = getattr(
    settings,
    "SIMPLECMS_DEFAULT_TEMPLATE",
    SIMPLECMS_TEMPLATE_CHOICES[0][0] if SIMPLECMS_TEMPLATE_CHOICES else None,
)


if not SIMPLECMS_TEMPLATE_CHOICES:
    raise ImproperlyConfigured("The 'SIMPLECMS_TEMPLATE_CHOICES' variable is not set!")

if not SIMPLECMS_DEFAULT_TEMPLATE:
    raise ImproperlyConfigured("The 'SIMPLECMS_DEFAULT_TEMPLATE' variable is not set!")
