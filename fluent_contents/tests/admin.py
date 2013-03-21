from pprint import pformat
from django.conf import settings
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User
from django.contrib.messages.middleware import MessageMiddleware
from django.core.urlresolvers import reverse
from django.test import RequestFactory
from fluent_contents.models import Placeholder
from fluent_contents.tests.testapp.admin import PlaceholderFieldTestPageAdmin
from fluent_contents.tests.testapp.models import PlaceholderFieldTestPage
from fluent_contents.tests.utils import AppTestCase, override_settings


class AdminTest(AppTestCase):
    """
    Test the admin functions.
    """

    def setUp(self):
        # Admin objects for all tests.
        self.factory = RequestFactory()
        self.admin_site = AdminSite()
        self.admin_user = User.objects.get(is_superuser=True)

        self.settings = override_settings(
            MIDDLEWARE_CLASSES = (
                'django.middleware.common.CommonMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.middleware.csrf.CsrfViewMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'django.contrib.messages.middleware.MessageMiddleware',
            )
        )
        self.settings.enable()


    def tearDown(self):
        self.settings.disable()


    def test_add_page(self):
        """
        Test adding an object with placeholder field via the admin.
        """
        self.admin_site.register(PlaceholderFieldTestPage, PlaceholderFieldTestPageAdmin)
        modeladmin = self.admin_site._registry[PlaceholderFieldTestPage]

        # Making a POST call with an unused ID should add the recipe.
        contents_slot = PlaceholderFieldTestPage.contents.slot
        formdata = self._get_management_form_data(modeladmin)
        formdata.update({
            'title': 'TEST1',
            'placeholder-fs-TOTAL_FORMS': '1',
            'placeholder-fs-0-slot': contents_slot,
            'placeholder-fs-0-role': Placeholder.MAIN,
        })
        response = self._post_add(modeladmin, formdata)
        self.assertEquals(response.status_code, 302, "No redirect, received: {0}".format(self._render_response(response)))

        # Check that the page exists.
        page = PlaceholderFieldTestPage.objects.get(title='TEST1')

        # Check that the placeholder is created.
        placeholder = page.contents
        self.assertEqual(placeholder.slot, contents_slot)
        self.assertEqual(placeholder.role, Placeholder.MAIN)


    def _post_add(self, modeladmin, formdata):
        opts = modeladmin.opts
        url = reverse('admin:{0}_{1}_add'.format(opts.app_label, opts.module_name))

        # Build request
        formdata['csrfmiddlewaretoken'] = 'foo'
        request = self.factory.post(url, data=formdata)
        request.COOKIES[settings.CSRF_COOKIE_NAME] = 'foo'

        # Add properties which middleware would typically do
        request.session = {}
        request.user = self.admin_user
        MessageMiddleware().process_request(request)

        # Make a direct call, circumvents login page.
        return modeladmin.add_view(request)


    def _get_management_form_data(self, modeladmin):
        """
        Return the formdata that the management forms need.
        """
        opts = modeladmin.opts
        url = reverse('admin:{0}_{1}_add'.format(opts.app_label, opts.module_name))
        request = self.factory.get(url)

        if hasattr(modeladmin, 'get_inline_instances'):
            inline_instances = modeladmin.get_inline_instances(request)  # Django 1.4
        else:
            inline_instances = [inline_class(modeladmin.model, self.admin_site) for inline_class in modeladmin.inlines]

        forms = []
        for inline_instance in inline_instances:
            FormSet = inline_instance.get_formset(request)
            formset = FormSet(instance=modeladmin.model())
            forms.append(formset.management_form)

        # In a primitive way, get the form fields.
        # This is not exactly the same as a POST, since that runs through clean()
        formdata = {}
        for form in forms:
            for boundfield in form:
                formdata[boundfield.html_name] = boundfield.value()

        return formdata


    def _render_response(self, response):
        if hasattr(response, 'render'):
            # TemplateResponse
            #return response.render().content
            return pformat(response.context_data)
        else:
            return response.content
