"""
The admin classes of `fluent_contents` provide the necessary integration with existing admin interfaces.

The placeholder interfaces are implemented by model admin inlines,
so they can be added to almost any admin interface.
To assist in configuring the admin interface properly, there are a few base classes:

* For models with a :class:`~fluent_contents.models.PlaceholderField`, use the :class:`PlaceholderFieldAdmin` as base class.
* For CMS models, use the :class:`PlaceholderEditorAdmin` as base class.

Both classes ensure the placeholders and inlines are properly setup.
"""
from django.contrib import admin
from fluent_contents.admin.placeholdereditor import PlaceholderEditorAdmin, PlaceholderEditorInline, PlaceholderEditorBaseMixin
from fluent_contents.admin.placeholderfield import PlaceholderFieldAdmin
from fluent_contents.admin.contentitems import get_content_item_inlines

__all__ = (
    'PlaceholderEditorAdmin', 'PlaceholderEditorInline', 'PlaceholderEditorBaseMixin', 'PlaceholderFieldAdmin',
    'get_content_item_inlines',
)
