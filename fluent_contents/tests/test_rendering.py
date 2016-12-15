from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import Template
from django.test import RequestFactory

from fluent_contents import rendering
from fluent_contents.extensions import PluginContext
from fluent_contents.models import Placeholder, DEFAULT_TIMEOUT
from fluent_contents.rendering import utils as rendering_utils
from fluent_contents.tests import factories
from fluent_contents.tests.testapp.models import TestPage, RawHtmlTestItem, TimeoutTestItem, OverrideBase, MediaTestItem, \
    RedirectTestItem
from fluent_contents.tests.utils import AppTestCase


class RenderingTests(AppTestCase):
    """
    Test cases for template tags
    """
    dummy_request = RequestFactory().get('/')
    install_apps = (
        'fluent_contents.tests.testapp',
    )

    # Most rendering tests happen in the "templatetags" tests.
    # These functions test the other constraints

    def test_render_timeout(self):
        """
        The ``render_placeholder`` should detect the maximum timeout that can be used for caching.
        """
        # Attach contents to the parent object.
        page2 = TestPage.objects.create(pk=9, contents="TEST2!")
        placeholder2 = Placeholder.objects.create_for_object(page2, 'slot2')
        RawHtmlTestItem.objects.create_for_placeholder(placeholder2, html='<b>Item1!</b>', sort_order=1)

        output = rendering.render_placeholder(self.dummy_request, placeholder2, parent_object=page2, cachable=False)
        self.assertEqual(output.html, '<b>Item1!</b>')
        self.assertEqual(output.cache_timeout, DEFAULT_TIMEOUT)

        item2 = TimeoutTestItem.objects.create_for_placeholder(placeholder2, html='<b>Item2!</b>', sort_order=1)
        output = rendering.render_placeholder(self.dummy_request, placeholder2, parent_object=page2, cachable=False)
        self.assertEqual(output.html, '<b>Item1!</b><b>Item2!</b>')
        self.assertEqual(output.cache_timeout, 60)  # this is that timeout that should be used for the placeholder cache item.

    def test_render_media(self):
        """
        Test that 'class FrontendMedia' works.
        """
        placeholder = factories.create_placeholder()
        factories.create_content_item(MediaTestItem, placeholder=placeholder, html='MEDIA_TEST')

        output = rendering.render_placeholder(self.dummy_request, placeholder)
        self.assertEqual(output.html.strip(), 'MEDIA_TEST')
        self.assertEqual(output.media._js, ['testapp/media_item.js'])
        self.assertEqual(output.media._css, {'screen': ['testapp/media_item.css']})

    def test_render_redirect(self):
        cache.clear()
        page = factories.create_page()
        placeholder = factories.create_placeholder(page=page)
        factories.create_content_item(RedirectTestItem, placeholder=placeholder, html='MEDIA_TEST')

        response = self.client.get(reverse('testpage', args=(page.pk,)))
        self.assertTrue(response.status_code, 301)
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue(response['Location'].endswith('/contact/success/'))

    def test_debug_is_method_overwritten(self):
        """
        Test the "is method overwritten" logic to detect template changes
        :return:
        :rtype:
        """
        class OverrideSame(OverrideBase):
            pass

        class OverrideReplace(OverrideBase):

            def get_render_template(self):
                pass

        self.assertFalse(rendering_utils._is_method_overwritten(OverrideSame(), OverrideBase, 'get_render_template'))
        self.assertTrue(rendering_utils._is_method_overwritten(OverrideReplace(), OverrideBase, 'get_render_template'))

    def test_render_csrf_token(self):
        """
        Rendered plugins should have access to the CSRF token
        """
        request = RequestFactory().get('/')
        request.META['CSRF_COOKIE'] = 'TEST1TEST2'  # Not literally used as of Django 1.10

        template = Template('{% csrf_token %}')
        context = PluginContext(request)
        self.assertTrue(context.get('csrf_token', None), 'csrf_token not found in context')
        self.assertNotEqual(str(context['csrf_token']), 'NOTPROVIDED', 'csrf_token is NOTPROVIDED')
        self.assertTrue('csrfmiddlewaretoken' in template.render(context), 'csrf_token not found in template')
