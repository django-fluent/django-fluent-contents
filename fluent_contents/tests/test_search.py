from fluent_contents.models import Placeholder
from fluent_contents.plugins.text.models import TextItem
from fluent_contents.tests.testapp.models import TestPage
from fluent_contents.tests.utils import AppTestCase


class SearchTest(AppTestCase):
    """
    Tests for search
    """

    def test_search_text(self):
        # Attach contents to the parent object.
        page2 = TestPage.objects.create(pk=20, contents="Search!")
        placeholder2 = Placeholder.objects.create_for_object(page2, 'slot2')
        TextItem.objects.create_for_placeholder(placeholder2, text=u'<b>Item1!</b>', sort_order=1)

        self.assertEqual(placeholder2.get_search_text().rstrip(), u"Item1!")
