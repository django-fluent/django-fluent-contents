"""
Utils for internal tests, and utils for testing third party plugins.
"""
from __future__ import print_function
from importlib import import_module

from django.contrib.auth import get_user_model
from django.contrib.admin import AdminSite
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.contrib.auth.models import User
from django.contrib.messages.middleware import MessageMiddleware
from future.builtins import str
from django.conf import settings
from django.core.management import call_command
from django.contrib.sites.models import Site
from django.test import TestCase, RequestFactory
from fluent_utils.django_compat import reverse

from fluent_contents import rendering
from fluent_contents.rendering.utils import get_dummy_request


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
                    from django.template.utils import get_app_template_dirs
                    get_app_template_dirs.cache_clear()

            if run_syncdb:
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

    def assertFormSuccess(self, request_url, response):
        """
        Assert that the response was a redirect, not a form error.
        """
        self.assertIn(response.status_code, [200, 302])
        if response.status_code != 302:
            context_data = response.context_data
            if 'errors' in context_data:
                errors = response.context_data['errors']
            elif 'form' in context_data:
                errors = context_data['form'].errors
            else:
                raise KeyError("Unknown field for errors in the TemplateResponse!")

            self.assertEqual(response.status_code, 302,
                             "Form errors in calling {0}:\n{1}".format(request_url, errors.as_text()))
        self.assertTrue('/login/?next=' not in response['Location'], "Received login response for {0}".format(request_url))


class AdminTestCase(AppTestCase):
    """
    Testing the creation of mail addresses
    """
    #: The model to test
    model = None
    #: The admin class to test
    admin_class = None

    @classmethod
    def setUpClass(cls):
        super(AdminTestCase, cls).setUpClass()

        # Have a separate site, to avoid dependency on polymorphic wrapping or standard admin configuration
        cls.admin_site = AdminSite()
        cls.admin_site.register(cls.model, cls.admin_class)
        cls.admin_instance = cls.admin_site._registry[cls.model]
        cls.admin_user = User.objects.create_superuser('admin', 'admin@example.org', password='admin')

    def get_add_url(self):
        return reverse(admin_urlname(self.admin_instance.opts, 'add'))

    def get_change_url(self, object_id):
        return reverse(admin_urlname(self.admin_instance.opts, 'change'), args=(object_id,))

    def get_delete_url(self, object_id):
        return reverse(admin_urlname(self.admin_instance.opts, 'delete'), args=(object_id,))

    def admin_post_add(self, formdata):
        """
        Make a direct "add" call to the admin page, circumvening login checks.
        """
        request = self.create_admin_request('post', self.get_add_url(), data=formdata)
        response = self.admin_instance.add_view(request)
        self.assertFormSuccess(request.path, response)
        return response

    def admin_get_change(self, object_id, query=None, **extra):
        """
        Perform a GET request on the admin page
        """
        request = self.create_admin_request('get', self.get_change_url(object_id), data=query, **extra)
        response = self.admin_instance.change_view(request, str(object_id))
        self.assertEqual(response.status_code, 200)
        return response

    def admin_post_change(self, object_id, formdata, **extra):
        """
        Make a direct "add" call to the admin page, circumvening login checks.
        """
        request = self.create_admin_request('post', self.get_change_url(object_id), data=formdata, **extra)
        response = self.admin_instance.change_view(request, str(object_id))
        self.assertFormSuccess(request.path, response)
        return response

    def admin_post_delete(self, object_id, **extra):
        """
        Make a direct "add" call to the admin page, circumvening login checks.
        """
        request = self.create_admin_request('post', self.get_delete_url(object_id), **extra)
        response = self.admin_instance.delete_view(request, str(object_id))
        self.assertEqual(response.status_code, 302, "Form errors in calling {0}".format(request.path))
        return response

    def create_admin_request(self, method, url, data=None, **extra):
        """
        Construct an Request instance for the admin view.
        """
        factory_method = getattr(RequestFactory(), method)

        if data is not None:
            if method != 'get':
                data['csrfmiddlewaretoken'] = 'foo'
            dummy_request = factory_method(url, data=data)
            dummy_request.user = self.admin_user

            # Add the management form fields if needed.
            #base_data = self._get_management_form_data(dummy_request)
            # base_data.update(data)
            #data = base_data

        request = factory_method(url, data=data, **extra)
        request.COOKIES[settings.CSRF_COOKIE_NAME] = 'foo'
        request.csrf_processing_done = True

        # Add properties which middleware would typically do
        request.session = {}
        request.user = self.admin_user
        MessageMiddleware().process_request(request)
        return request

    def _get_management_form_data(self, request):
        """
        Return the formdata that the management forms need.
        """
        inline_instances = self.admin_instance.get_inline_instances(request)
        forms = []
        for inline_instance in inline_instances:
            FormSet = inline_instance.get_formset(request)
            formset = FormSet(instance=self.admin_instance.model())
            forms.append(formset.management_form)

        # In a primitive way, get the form fields.
        # This is not exactly the same as a POST, since that runs through clean()
        formdata = {}
        for form in forms:
            for boundfield in form:
                formdata[boundfield.html_name] = boundfield.value()

        return formdata
