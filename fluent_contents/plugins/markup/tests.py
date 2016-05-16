from django.test import TestCase
from django.utils.encoding import force_text

from fluent_contents.plugins.markup.models import LANGUAGE_MODEL_CLASSES
from fluent_contents.tests.factories import create_content_item
from fluent_contents.tests.utils import render_content_items


class MarkupPluginTests(TestCase):
    """
    Testing markup plugin logic
    """

    def test_markup(self):
        RstItem = LANGUAGE_MODEL_CLASSES['restructuredtext']

        item = create_content_item(RstItem, text="""
RST
----

* Markup!""")

        expected = '''<div class="markup"><h1 class="title">RST</h1><ul class="simple"><li>Markup!</li></ul></div>'''
        self.assertHTMLEqual(force_text(render_content_items([item])), expected)
