from __future__ import print_function
import html5lib
from unittest import TestCase
from django_wysiwyg.utils import clean_html, sanitize_html


class TextPluginTests(TestCase):
    """
    Test whether the sanitation works as expected.
    """
    HTML1_ORIGINAL  = u'<p><img src="/media/image.jpg" alt="" width="460" height="300" />&nbsp;&nbsp;<img style="float: left;" src="/media/image2.jpg" alt="" width="460" height="130" /></p><p>&nbsp;</p>'

    def test_broken_html5lib(self):
        """
        Test againt https://github.com/html5lib/html5lib-python/issues/189
        """
        msg = "This version of html5lib is known to break relative URLs!\nUse version 0.999 instead."
        self.assertTrue(html5lib.__version__ not in ['1.0b5', '1.0b6', '0.9999', '0.99999'], msg)

    def test_clean_html5lib(self):
        """
        Test how clean performs.
        """
        cleaned = clean_html(self.HTML1_ORIGINAL)
        self.assertTrue('460' in cleaned, u"Missing elements in {0}".format(cleaned))
        self.assertTrue('float: left' in cleaned, u"Missing elements in {0}".format(cleaned))
        self.assertTrue('/media/image.jpg' in cleaned, u"Missing elements in {0}".format(cleaned))
        self.assertTrue('/media/image2.jpg' in cleaned, u"Missing elements in {0}".format(cleaned))

    def test_sanitize_html5lib(self):
        """
        Test whether the sanitize feature doesn't completely break pages.
        """
        sanitized = sanitize_html(self.HTML1_ORIGINAL)
        self.assertTrue('460' in sanitized, u"Missing elements in {0}".format(sanitized))
        self.assertTrue('float: left' in sanitized, u"Missing elements in {0}".format(sanitized))
        self.assertTrue('/media/image.jpg' in sanitized, u"Missing elements in {0}".format(sanitized))
        self.assertTrue('/media/image2.jpg' in sanitized, u"Missing elements in {0}".format(sanitized))
