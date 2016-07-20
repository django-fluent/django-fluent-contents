import django
from django.contrib.contenttypes.models import ContentType

from fluent_contents.models import ContentItem
from fluent_contents.tests.utils import AppTestCase


class ModelTests(AppTestCase):
    """
    Testing the data model.
    """

    def test_stale_model_str(self):
        """
        No matter what, the ContentItem.__str__() should work.
        This would break the admin delete screen otherwise.
        """
        c = ContentType()
        if django.VERSION >= (1, 8):
            c.save()
        a = ContentItem(polymorphic_ctype=c)
        self.assertEqual(str(a), "'(type deleted) 0' in 'None None'")
