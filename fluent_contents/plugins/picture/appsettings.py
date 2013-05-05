from django.conf import settings

FLUENT_PICTURE_UPLOAD_TO = getattr(settings, 'FLUENT_PICTURE_UPLOAD_TO', '.')
