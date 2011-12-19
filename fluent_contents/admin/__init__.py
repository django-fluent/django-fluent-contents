from django.contrib import admin
from fluent_contents.admin.placeholdereditor import PlaceholderEditorAdminMixin, PlaceholderEditorAdmin, PlaceholderEditorInline
from fluent_contents.admin.placeholderfield import PlaceholderFieldAdmin, PlaceholderFieldAdminMixin
from fluent_contents.admin.contentitems import get_content_item_inlines

__all__ = (
    'PlaceholderEditorAdminMixin', 'PlaceholderEditorAdmin', 'PlaceholderEditorInline',
    'PlaceholderFieldAdmin', 'PlaceholderFieldAdminMixin',
    'get_content_item_inlines',
)


from fluent_contents.admin.debug import PlaceholderAdmin
from fluent_contents.models.db import Placeholder, ContentItem
admin.site.register(Placeholder, PlaceholderAdmin)
admin.site.register(ContentItem)
