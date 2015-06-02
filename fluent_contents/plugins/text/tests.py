from unittest import TestCase
from django_wysiwyg.utils import clean_html, sanitize_html



class TextPluginTests(TestCase):
    """
    Test whether the sanitation works as expected.
    """
    HTML1_ORIGINAL  = u'<p><img src="/media/image.jpg" alt="" width="460" height="300" />&nbsp;&nbsp;<img style="float: left;" src="/media/image2.jpg" alt="" width="460" height="130" /></p><p>&nbsp;</p>'
    HTML1_CLEANED   = u'<p><img height=300 src=/media/image.jpg width=460 alt="">\xa0\xa0<img height=130 style="float: left;" src=/media/image2.jpg width=460 alt=""></p><p>\xa0</p>'
    HTML1_SANITIZED = u'<p><img height=300 width=460 src=/media/image.jpg alt="">\xa0\xa0<img height=130 alt="" width=460 src=/media/image2.jpg style="float: left;"></p><p>\xa0</p>'

    def test_clean_html5lib(self):
        """
        Test how clean performs.
        """
        clean = clean_html(self.HTML1_ORIGINAL)
        self.assertEqual(_normalize_html(clean), _normalize_html(self.HTML1_CLEANED))

    def test_sanitize_html5lib(self):
        """
        Test whether the sanitize feature doesn't completely break pages.
        """
        # This also tests againt https://github.com/html5lib/html5lib-python/issues/189
        self.assertEqual(_normalize_html(sanitize_html(self.HTML1_ORIGINAL)), _normalize_html(self.HTML1_SANITIZED))


def _normalize_html(html):
    # Allow minor changes
    return sorted(html.split(' '))
