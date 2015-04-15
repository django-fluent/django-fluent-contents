from django.test import RequestFactory
from fluent_contents import rendering
from fluent_contents.models import Placeholder, DEFAULT_TIMEOUT
from fluent_contents.tests.testapp.models import TestPage, RawHtmlTestItem, TimeoutTestItem
from fluent_contents.tests.utils import AppTestCase


class RenderingTests(AppTestCase):
    """
    Test cases for template tags
    """
    dummy_request = RequestFactory().get('/')
    install_apps = (
        'fluent_contents.tests.testapp',
    )


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
