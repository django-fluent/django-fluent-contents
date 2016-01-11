from pprint import pprint
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.template import Template, Context, VariableDoesNotExist, TemplateSyntaxError
from django.test import RequestFactory
from template_analyzer import get_node_instances

from fluent_contents import appsettings
from fluent_contents.models import Placeholder
from fluent_contents.templatetags.fluent_contents_tags import PagePlaceholderNode
from fluent_contents.tests.testapp.models import TestPage, RawHtmlTestItem, PlaceholderFieldTestPage
from fluent_contents.tests.utils import AppTestCase
from fluent_contents.analyzer import get_template_placeholder_data


class TemplateTagTests(AppTestCase):
    """
    Test cases for template tags
    """
    dummy_request = RequestFactory().get('/')
    dummy_request.user = AnonymousUser()
    install_apps = (
        'fluent_contents.tests.testapp',
    )

    def test_page_placeholder_metadata(self):
        """
        The ``page_placeholder`` tag should expose metadata, which ``fluent_contents.analyzer`` can read.
        """
        template = Template("""{% load fluent_contents_tags %}{% page_placeholder page "slot1" title="SlotTest1" role="s" %}""")

        # Test raw Placeholder extraction
        raw_placeholders = get_node_instances(template, PagePlaceholderNode)
        self.assertEqual(len(raw_placeholders), 1)
        self.assertEqual(raw_placeholders[0].get_slot(), 'slot1')
        self.assertEqual(raw_placeholders[0].get_title(), 'SlotTest1')
        self.assertEqual(raw_placeholders[0].get_role(), 's')

        # Now test the public API, that returns PlaceholderData objects.
        data = get_template_placeholder_data(template)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].slot, 'slot1')
        self.assertEqual(data[0].title, 'SlotTest1')
        self.assertEqual(data[0].role, 's')

        # Test2: fallback code
        template = Template("""{% load fluent_contents_tags %}{% page_placeholder page "slot_test2" %}""")

        # Test raw Placeholder extraction
        raw_placeholders = get_node_instances(template, PagePlaceholderNode)
        self.assertEqual(len(raw_placeholders), 1)
        self.assertEqual(raw_placeholders[0].get_slot(), 'slot_test2')
        self.assertEqual(raw_placeholders[0].get_title(), 'Slot Test2')
        self.assertEqual(raw_placeholders[0].get_role(), None)

        # Test the public API
        data = get_template_placeholder_data(template)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].slot, 'slot_test2')
        self.assertEqual(data[0].title, 'Slot Test2')
        self.assertEqual(data[0].role, 'm')  # Defaults to "main"

    def test_page_placeholder(self):
        """
        The ``page_placeholder`` tag should render the content associated with it.
        """
        # Attach contents to the parent object.
        page1 = TestPage.objects.create(contents="TEST!")
        placeholder1 = Placeholder.objects.create_for_object(page1, 'slot1')
        item1 = RawHtmlTestItem.objects.create_for_placeholder(placeholder1, html='<b>Item1!</b>', sort_order=1)
        item2 = RawHtmlTestItem.objects.create_for_placeholder(placeholder1, html='<b>Item2!</b>', sort_order=2)

        # Test standard output
        html = self._render("""{% load fluent_contents_tags %}{% page_placeholder page1 "slot1" %}""", {'page1': page1})
        self.assertEqual(html, u'<b>Item1!</b><b>Item2!</b>')

        # Test standard output + template variable
        html = self._render("""{% load fluent_contents_tags %}{% page_placeholder page1 "slot1" template="testapp/placeholder_splitter.html" %}""", {'page1': page1})
        self.assertEqual(html.replace('\n', ''), u'<b>Item1!</b><div class="splitter"></div><b>Item2!</b>')

        # Test if the "page" variable is used as default argument
        html = self._render("""{% load fluent_contents_tags %}{% page_placeholder "slot1" %}""", {'page': page1})
        self.assertEqual(html, u'<b>Item1!</b><b>Item2!</b>')

        # Test of invalid slots fail silently. Give the user the chance to enter the data in the CMS.
        html = self._render("""{% load fluent_contents_tags %}{% page_placeholder page1 "invalid_slot1" %}""", {'page1': page1})
        self.assertEqual(html, u"<!-- placeholder 'invalid_slot1' does not yet exist -->")

        # Test if a missing "page" variable fails.
        self.assertRaises(VariableDoesNotExist, lambda: self._render("""{% load fluent_contents_tags %}{% page_placeholder "slot1" %}""", {}))

        # Test if a missing arguments are reported
        self.assertRaises(TemplateSyntaxError, lambda: Template("""{% load fluent_contents_tags %}{% page_placeholder %}"""))
        self.assertRaises(TemplateSyntaxError, lambda: Template("""{% load fluent_contents_tags %}{% page_placeholder arg1 arg2 arg3 %}"""))

    def test_render_placeholder(self):
        """
        The ``render_placeholder`` tag should render objects by reference.
        """
        # Attach contents to the parent object.
        page2 = PlaceholderFieldTestPage.objects.create()
        placeholder1 = Placeholder.objects.create_for_object(page2, 'field_slot1')
        item1 = RawHtmlTestItem.objects.create_for_placeholder(placeholder1, html='<b>Item1!</b>', sort_order=1)
        item2 = RawHtmlTestItem.objects.create_for_placeholder(placeholder1, html='<b>Item2!</b>', sort_order=2)

        # Make sure the unittests won't succeed because of cached output.
        appsettings.FLUENT_CONTENTS_CACHE_OUTPUT = False
        cache.clear()

        # Test standard behavior, with an object reference
        # - fetch ContentItem
        # - fetch RawHtmlTestItem
        with self.assertNumQueries(2) as ctx:
            html = self._render("""{% load fluent_contents_tags %}{% render_placeholder placeholder1 %}""", {'placeholder1': placeholder1})
            self.assertEqual(html, u'<b>Item1!</b><b>Item2!</b>')

        # Test passing Placeholder via PlaceholderField (actually tests the PlaceholderFieldDescriptor)
        # - fetch Placeholder
        # - fetch ContentItem
        # - fetch RawHtmlTestItem
        with self.assertNumQueries(3) as ctx:
            html = self._render("""{% load fluent_contents_tags %}{% render_placeholder page2.contents %}""", {'page2': page2})
            self.assertEqual(html, u'<b>Item1!</b><b>Item2!</b>')

        # Test passing a related object manager.
        # - fetch Placeholder
        # - parent is taken from RelatedManager
        # - fetch ContentItem
        # - fetch RawHtmlTestItem
        with self.assertNumQueries(3) as ctx:
            html = self._render("""{% load fluent_contents_tags %}{% render_placeholder page2.placeholder_set %}""", {'page2': page2})
            self.assertEqual(html, u'<b>Item1!</b><b>Item2!</b>')

        # Test if None values fail silently
        with self.assertNumQueries(0) as ctx:
            html = self._render("""{% load fluent_contents_tags %}{% render_placeholder none_object %}""", {'none_object': None})
            self.assertEqual(html, u'<!-- placeholder object is None -->')

        # Test if invalid objects are reported.
        # This requires `TEMPLATE_DEBUG = False` in Django 1.3
        self.assertRaises(ValueError, lambda: self._render("""{% load fluent_contents_tags %}{% render_placeholder 123 %}""", {}))
        self.assertRaises(ValueError, lambda: self._render("""{% load fluent_contents_tags %}{% render_placeholder int_object %}""", {'int_object': 456}))

        # Test if a missing arguments are reported
        self.assertRaises(TemplateSyntaxError, lambda: Template("""{% load fluent_contents_tags %}{% render_placeholder %}"""))
        self.assertRaises(TemplateSyntaxError, lambda: Template("""{% load fluent_contents_tags %}{% render_placeholder arg1 arg2 %}"""))

    def test_num_item_queries(self):
        page3 = PlaceholderFieldTestPage.objects.create()
        placeholder1 = Placeholder.objects.create_for_object(page3, 'field_slot1')
        item1 = RawHtmlTestItem.objects.create_for_placeholder(placeholder1, html='<b>Item1!</b>', sort_order=1)
        item2 = RawHtmlTestItem.objects.create_for_placeholder(placeholder1, html='<b>Item2!</b>', sort_order=2)

        appsettings.FLUENT_CONTENTS_CACHE_OUTPUT = True
        appsettings.FLUENT_CONTENTS_CACHE_PLACEHOLDER_OUTPUT = False  # No full caching
        cache.clear()

        # First time:
        # - fetch ContentItem
        # - fetch RawHtmlTestItem
        with self.assertNumQueries(2) as ctx:
            self._render("""{% load fluent_contents_tags %}{% render_placeholder placeholder1 %}""", {'placeholder1': placeholder1})
            #pprint(ctx.captured_queries)

        # Second time
        # - fetch ContentItem
        with self.assertNumQueries(1) as ctx:
            self._render("""{% load fluent_contents_tags %}{% render_placeholder placeholder1 %}""", {'placeholder1': placeholder1})
            #pprint(ctx.captured_queries)

        # Using page_placeholder
        # - fetch Placeholder
        # - fetch ContentItem
        with self.assertNumQueries(2) as ctx:
            self._render("""{% load fluent_contents_tags %}{% page_placeholder 'field_slot1' %}""", {'page': page3})
            #pprint(ctx.captured_queries)

        # Using page_placeholder, use fallback
        # - fetch Placeholder
        # - fetch ContentItem
        # - fetch ContentItem fallback
        with self.assertNumQueries(2) as ctx:
            self._render("""{% load fluent_contents_tags %}{% page_placeholder 'field_slot1' fallback=True %}""", {'page': page3})
            #pprint(ctx.captured_queries)

    def test_num_placeholder_queries(self):
        page3 = PlaceholderFieldTestPage.objects.create()
        placeholder1 = Placeholder.objects.create_for_object(page3, 'field_slot1')
        item1 = RawHtmlTestItem.objects.create_for_placeholder(placeholder1, html='<b>Item1!</b>', sort_order=1)
        item2 = RawHtmlTestItem.objects.create_for_placeholder(placeholder1, html='<b>Item2!</b>', sort_order=2)

        appsettings.FLUENT_CONTENTS_CACHE_OUTPUT = True
        appsettings.FLUENT_CONTENTS_CACHE_PLACEHOLDER_OUTPUT = True
        cache.clear()

        # First time:
        # - fetch ContentItem
        # - fetch RawHtmlTestItem
        with self.assertNumQueries(2) as ctx:
            self._render("""{% load fluent_contents_tags %}{% render_placeholder placeholder1 %}""", {'placeholder1': placeholder1})
            #pprint(ctx.captured_queries)

        # Second time
        with self.assertNumQueries(0) as ctx:
            self._render("""{% load fluent_contents_tags %}{% render_placeholder placeholder1 %}""", {'placeholder1': placeholder1})
            #pprint(ctx.captured_queries)

        # Using page_placeholder
        with self.assertNumQueries(0) as ctx:
            self._render("""{% load fluent_contents_tags %}{% page_placeholder 'field_slot1' %}""", {'page': page3})
            #pprint(ctx.captured_queries)

        # Using page_placeholder, use fallback
        with self.assertNumQueries(0) as ctx:
            self._render("""{% load fluent_contents_tags %}{% page_placeholder 'field_slot1' fallback=True %}""", {'page': page3})
            #pprint(ctx.captured_queries)

    def _render(self, template_code, context_data):
        """
        Render a template
        """
        template = Template(template_code)
        context = Context(context_data)
        context['request'] = self.dummy_request
        return template.render(context)
