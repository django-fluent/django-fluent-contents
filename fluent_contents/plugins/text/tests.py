from unittest import TestCase

import html5lib

from fluent_contents.models import ContentItemManager
from fluent_contents.models.managers import ContentItemQuerySet
from fluent_contents.plugins.text.models import TextItem
from fluent_contents.utils.html import clean_html


class TextPluginTests(TestCase):
    """
    Test whether the sanitation works as expected.
    """

    HTML1_ORIGINAL = '<p><img src="/media/image.jpg" alt="" width="460" height="300" />&nbsp;&nbsp;<img style="float: left;" src="/media/image2.jpg" alt="" width="460" height="130" /></p><p>&nbsp;</p>'

    def test_default_manager(self):
        """
        Test that the default manager is correct.
        """
        self.assertIsInstance(TextItem.objects, ContentItemManager)
        self.assertIsInstance(TextItem.objects.all(), ContentItemQuerySet)

    def test_broken_html5lib(self):
        """
        Test againt https://github.com/html5lib/html5lib-python/issues/189
        """
        msg = (
            "This version of html5lib is known to break relative URLs!\nUse version 0.999 instead."
        )
        self.assertTrue(html5lib.__version__ not in ["1.0b5", "1.0b6", "0.9999", "0.99999"], msg)

    def test_clean_html5lib(self):
        """
        Test how clean performs.
        """
        cleaned = clean_html(self.HTML1_ORIGINAL)
        self.assertTrue("460" in cleaned, f"Missing elements in {cleaned}")
        self.assertTrue("float: left" in cleaned, f"Missing elements in {cleaned}")
        self.assertTrue("/media/image.jpg" in cleaned, f"Missing elements in {cleaned}")
        self.assertTrue("/media/image2.jpg" in cleaned, f"Missing elements in {cleaned}")

    def test_sanitize_html5lib(self):
        """
        Test whether the sanitize feature doesn't completely break pages.
        """
        sanitized = clean_html(self.HTML1_ORIGINAL, sanitize=True)
        self.assertTrue("460" in sanitized, f"Missing elements in {sanitized}")
        self.assertTrue("float: left" in sanitized, f"Missing elements in {sanitized}")
        self.assertTrue(
            "/media/image.jpg" in sanitized,
            f"Missing elements in {sanitized}",
        )
        self.assertTrue(
            "/media/image2.jpg" in sanitized,
            f"Missing elements in {sanitized}",
        )
