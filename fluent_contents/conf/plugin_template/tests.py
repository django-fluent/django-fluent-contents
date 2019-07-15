from django.test import TestCase

from fluent_contents.tests.factories import create_content_item
from fluent_contents.tests.utils import render_content_items

from .models import {{ model }}


class Test{{ plugin }}(TestCase):
    """
    Testing the CMS plugin.
    """

    def test_rendering(self):
        """
        Test the standard button
        """
        item = create_content_item({{ model }}, title="TEST1")
        output = render_content_items([item])
        self.assertIn('TEST1', output.html)
