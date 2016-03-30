from django.middleware.csrf import get_token
from django.template import Template
from django.test import RequestFactory
from fluent_contents import rendering
from fluent_contents.extensions import PluginContext
from fluent_contents.models import Placeholder, DEFAULT_TIMEOUT
from fluent_contents.rendering import utils as rendering_utils
from fluent_contents.tests.testapp.models import TestPage, RawHtmlTestItem, TimeoutTestItem, OverrideBase
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
        request.META['CSRF_COOKIE'] = 'TEST1TEST2'

        template = Template('{% csrf_token %}')
        context = PluginContext(request)
        self.assertTrue(context.get('csrf_token', None), 'csrf_token not found in context')
        self.assertNotEqual(str(context['csrf_token']), 'NOTPROVIDED', 'csrf_token is NOTPROVIDED')
        self.assertTrue('TEST1TEST2' in template.render(context), 'csrf_token not found in template')
