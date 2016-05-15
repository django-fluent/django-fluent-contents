from fluent_contents.models import Placeholder
from fluent_contents.tests.testapp.models import PlaceholderFieldTestPage


def create_page(title='foo'):
    """
    Create an page where contents can be placed at
    """
    return PlaceholderFieldTestPage.objects.create(title=title)


def create_placeholder(page=None, slot=None):
    """
    Create a placeholder for the contents.
    """
    if page is None:
        page = create_page()

    return Placeholder.objects.create_for_object(page, slot='field_slot1')


def create_content_item(ContentItemModel, placeholder=None, sort_order=1, language_code=None, **item_kwargs):
    """
    Create an Content Item to render
    """
    if placeholder is None:
        placeholder = create_placeholder()

    return ContentItemModel.objects.create_for_placeholder(
        placeholder,
        sort_order=sort_order,
        language_code=language_code,
        **item_kwargs
    )
