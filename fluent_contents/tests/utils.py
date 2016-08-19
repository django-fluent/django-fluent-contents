"""
Utils for internal tests, and utils for testing third party plugins.
"""
from __future__ import print_function
import django
from future.builtins import str
from django.conf import settings
from django.core.management import call_command
from django.contrib.sites.models import Site
from django.test import TestCase
from fluent_utils.django_compat import get_user_model
import os

from fluent_contents import rendering
from fluent_contents.rendering.utils import get_dummy_request

try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module  # Python 2.6


__all__ = (
    # Utils for testing third party plugins.
    'render_content_items',
    'get_dummy_request',

    # For internal tests:
    'AppTestCase',
)


def render_content_items(items, request=None, language=None, template_name=None, cachable=False):
    """
    Render a content items with settings well suited for testing.
    """
    if request is None:
        request = get_dummy_request(language=language)

    return rendering.render_content_items(request, items, template_name=template_name, cachable=cachable)


class AppTestCase(TestCase):
    """
    Tests for URL resolving.
    """
    user = None
    install_apps = (
        'fluent_contents.tests.testapp',
        'fluent_contents.plugins.sharedcontent',
        'fluent_contents.plugins.picture',
        'fluent_contents.plugins.text',
    )

    @classmethod
    def setUpClass(cls):
        super(AppTestCase, cls).setUpClass()

        # Avoid early import, triggers AppCache
        User = get_user_model()

        if cls.install_apps:
            # When running this app via `./manage.py test fluent_pages`, auto install the test app + models.
            run_syncdb = False
            for appname in cls.install_apps:
                if appname not in settings.INSTALLED_APPS:
                    print('Adding {0} to INSTALLED_APPS'.format(appname))
                    settings.INSTALLED_APPS = (appname,) + tuple(settings.INSTALLED_APPS)
                    run_syncdb = True

                    testapp = import_module(appname)

                    # Flush caches
                    if django.VERSION < (1, 9):
                        from django.template.loaders import app_directories
                        from django.db.models import loading
                        loading.cache.loaded = False

                        app_directories.app_template_dirs += (
                            os.path.join(os.path.dirname(testapp.__file__), 'templates'),
                        )
                    else:
                        from django.template.utils import get_app_template_dirs
                        get_app_template_dirs.cache_clear()

            if run_syncdb:
                if django.VERSION < (1, 7):
                    call_command('syncdb', verbosity=0)  # may run south's overlaid version
                else:
                    call_command('migrate', verbosity=0)

        # Create basic objects
        # 1.4 does not create site automatically with the defined SITE_ID, 1.3 does.
        Site.objects.get_or_create(id=settings.SITE_ID, defaults=dict(domain='django.localhost', name='django at localhost'))
        cls.user, _ = User.objects.get_or_create(is_superuser=True, is_staff=True, username="fluent-contents-admin")

    def assert200(self, url, msg_prefix=''):
        """
        Test that an URL exists.
        """
        if msg_prefix:
            msg_prefix += ": "
        self.assertEqual(self.client.get(url).status_code, 200, str(msg_prefix) + u"Page at {0} should be found.".format(url))

    def assert404(self, url, msg_prefix=''):
        """
        Test that an URL does not exist.
        """
        if msg_prefix:
            msg_prefix += ": "
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404, str(msg_prefix) + u"Page at {0} should return 404, got {1}.".format(url, response.status_code))
