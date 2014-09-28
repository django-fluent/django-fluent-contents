import django
if django.VERSION >= (1,7):
    raise DeprecationWarning(
        ""
        "South does not support Django 1.7. To upgrade this project:\n"
        "- Use Django 1.6 to apply the latest South migrations\n"
        "- Then upgrade to Django 1.7\n"
        "- Finally remove south from INSTALLED_APPS\n"
    )
