from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.contrib.contenttypes.models import ContentType
from django.test import override_settings
from django.utils import six

from fluent_contents.models import Placeholder
from fluent_contents.tests import factories
from fluent_contents.tests.testapp.admin import PlaceholderFieldTestPageAdmin
from fluent_contents.tests.testapp.models import PlaceholderFieldTestPage, \
    RawHtmlTestItem, TimeoutTestItem
from fluent_contents.tests.utils import AdminTestCase


class AdminTest(AdminTestCase):
    """
    Test the admin functions.
    """
    model = PlaceholderFieldTestPage
    admin_class = PlaceholderFieldTestPageAdmin

    def setUp(self):
        self.settings = override_settings(
            MIDDLEWARE_CLASSES = (
                'django.middleware.common.CommonMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.middleware.csrf.CsrfViewMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'django.contrib.messages.middleware.MessageMiddleware',
            )
        )
        self.settings.enable()

    def tearDown(self):
        self.settings.disable()

    def test_add_page(self):
        """
        Test adding an object with placeholder field via the admin.
        """
        # Get all post data.
        # Includes all inlines, so all inline formsets of other plugins will be added (with TOTAL_FORMS 0)
        contents_slot = PlaceholderFieldTestPage.contents.slot
        formdata = {
            'title': 'TEST1',
            'language_code': 'nl',
            'placeholder-fs-INITIAL_FORMS': 0,
            'placeholder-fs-MIN_NUM_FORMS': 0,
            'placeholder-fs-MAX_NUM_FORMS': 1000,
            'placeholder-fs-TOTAL_FORMS': '1',
            'placeholder-fs-0-slot': contents_slot,
            'placeholder-fs-0-role': Placeholder.MAIN,
            'contentitem-TOTAL_FORMS': '1',
            'contentitem-MAX_NUM_FORMS': '',
            'contentitem-INITIAL_FORMS': '0',
            'contentitem-0-polymorphic_ctype': ContentType.objects.get_for_model(RawHtmlTestItem).pk,
            'contentitem-0-placeholder': '',                   # The placeholder is not defined yet, as item is not yet created.
            'contentitem-0-placeholder_slot': contents_slot,   # BaseContentItemFormSet resolves the placeholder after it's created
            'contentitem-0-sort_order': '1',
            'contentitem-0-html': u'<b>foo</b>',
        }

        # Make a POST to the admin page.
        self.admin_post_add(formdata)

        # Check that the page exists.
        page = PlaceholderFieldTestPage.objects.get(title='TEST1')

        # Check that the placeholder is created,
        # and properly links back to it's parent.
        placeholder = page.contents
        self.assertEqual(placeholder.slot, contents_slot)
        self.assertEqual(placeholder.role, Placeholder.MAIN)
        self.assertEqual(placeholder.parent, page)

        # Check that the ContentItem is created,
        # and properly links back to it's parent.
        rawhtmltestitem = RawHtmlTestItem.objects.get(html=u'<b>foo</b>')
        self.assertEqual(rawhtmltestitem.placeholder, placeholder)
        self.assertEqual(rawhtmltestitem.parent, page)

        # Also check reverse relation of placeholder
        rawhtmltestitem = placeholder.contentitems.all()[0]
        self.assertEqual(rawhtmltestitem.html, u'<b>foo</b>')

    def test_change_page(self):
        """
        Testing how the change page works
        """
        # Create item outside Django admin
        slot = PlaceholderFieldTestPage.contents.slot
        page = PlaceholderFieldTestPage.objects.create(title='TEST2')
        placeholder = Placeholder.objects.create_for_object(page, slot, role='m')
        item1 = RawHtmlTestItem.objects.create_for_placeholder(placeholder, language_code='en', html='<b>foo</b>')

        # Fetch the page
        response = self.admin_get_change(page.pk)

        # Collect all existing inputs
        formdata = {}
        formdata.update(response.context_data['adminform'].form.initial)
        for inline_admin_formset in response.context_data['inline_admin_formsets']:
            for boundfield in inline_admin_formset.formset.management_form:
                formdata[boundfield.html_name] = boundfield.value()

            for form in inline_admin_formset.formset.forms:
                for boundfield in form:
                    formdata[boundfield.html_name] = boundfield.value()

        self.assertEqual(formdata, {
            'title': u'TEST2',
            'contents': 1,
            'placeholder-fs-INITIAL_FORMS': 1,
            'placeholder-fs-MIN_NUM_FORMS': 0,
            'placeholder-fs-MAX_NUM_FORMS': 1000,
            'placeholder-fs-TOTAL_FORMS': 1,
            'placeholder-fs-0-DELETE': None,
            'placeholder-fs-0-id': placeholder.pk,
            'placeholder-fs-0-role': u'm',
            'placeholder-fs-0-slot': u'field_slot1',
            'placeholder-fs-0-title': u'Field Slot1',
            'contentitem-INITIAL_FORMS': 1,
            'contentitem-TOTAL_FORMS': 1,
            'contentitem-MIN_NUM_FORMS': 0,
            'contentitem-MAX_NUM_FORMS': 1000,
            'contentitem-0-DELETE': None,
            'contentitem-0-html': u'<b>foo</b>',
            'contentitem-0-id': item1.pk,
            'contentitem-0-parent_item': None,
            'contentitem-0-parent_item_uid': 1,
            'contentitem-0-placeholder': 1,
            'contentitem-0-placeholder_slot': None,
            'contentitem-0-polymorphic_ctype': item1.polymorphic_ctype_id,
            'contentitem-0-sort_order': 1,
        })

        # Update the items, adding a new one
        formdata.update({
            'contentitem-TOTAL_FORMS': 2,
            'contentitem-1-html': u'<b>bar</b>',
            'contentitem-1-id': None,
            'contentitem-1-parent_item': None,
            'contentitem-1-parent_item_uid': 1,
            'contentitem-1-placeholder': None,
            'contentitem-1-placeholder_slot': slot,
            'contentitem-1-polymorphic_ctype': ContentType.objects.get_for_model(TimeoutTestItem).pk,
            'contentitem-1-sort_order': 2,
        })

        for key, value in six.iteritems(formdata):
            if value is None:
                formdata[key] = ''

        response = self.admin_post_change(page.pk, formdata)

        # Must have created two items
        self.assertEqual([item.html for item in placeholder.contentitems.all()], [u'<b>foo</b>', u'<b>bar</b>'])
        item2 = placeholder.contentitems.all()[1]
        self.assertEqual(item2.placeholder, placeholder)
        self.assertEqual(item2.parent, page)
        self.assertEqual(item2.html, u'<b>bar</b>')

    def test_copy_language_backend(self):
        """
        Testing how the copy button works.
        It calls the ``get_placeholder_data_view`` function.
        """
        page = factories.create_page()
        placeholder = factories.create_placeholder(page=page)
        item1 = factories.create_content_item(RawHtmlTestItem, placeholder=placeholder, html='AA')
        item2 = factories.create_content_item(RawHtmlTestItem, placeholder=placeholder, html='BB')

        request = self.create_admin_request('post', admin_urlname(page._meta, 'get_placeholder_data'))
        data = self.admin_instance.get_placeholder_data_view(request, page.pk).jsondata
        self.assertEqual(len(data['formset_forms']), 2)
        self.assertEqual(data['formset_forms'][0]['model'], 'RawHtmlTestItem')
        self.assertEqual(data['formset_forms'][0]['contentitem_id'], item1.pk)
        self.assertEqual(data['formset_forms'][1]['contentitem_id'], item2.pk)
        self.assertTrue('AA' in data['formset_forms'][0]['html'])
