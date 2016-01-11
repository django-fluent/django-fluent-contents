from fluent_contents.models import Placeholder
from fluent_contents.plugins.picture.models import PictureItem
from fluent_contents.plugins.text.models import TextItem
from fluent_contents.tests.testapp.models import TestPage, RawHtmlTestItem
from fluent_contents.tests.utils import AppTestCase


class SearchTest(AppTestCase):
    """
    Tests for search
    """

    def test_search_text(self):
        """
        Test: Simple text indexing should work. HTML is stripped.
        """
        page = TestPage.objects.create(pk=20, contents="Search!")
        placeholder = Placeholder.objects.create_for_object(page, 'slot2')
        TextItem.objects.create_for_placeholder(placeholder, text=u'<b>Item1!</b>', sort_order=1)

        self.assertEqual(placeholder.get_search_text().rstrip(), u"Item1!")

    def test_search_skip(self):
        """
        Test: Search should skip elements without search_fields or search_output
        """
        page = TestPage.objects.create(pk=20, contents="Search!")
        placeholder = Placeholder.objects.create_for_object(page, 'slot2')

        RawHtmlTestItem.objects.create_for_placeholder(placeholder, html=u"<b>HTML!!</b>", sort_order=2)
        self.assertEqual(placeholder.get_search_text(), u"")

    def test_search_fields(self):
        """
        Test: Search should skip elements without search_fields or search_output
        """
        page = TestPage.objects.create(pk=20, contents="Search!")
        placeholder = Placeholder.objects.create_for_object(page, 'slot2')

        PictureItem.objects.create_for_placeholder(placeholder, caption=u"<b>caption</b>", sort_order=1)
        self.assertEqual(placeholder.get_search_text(), u"caption")
