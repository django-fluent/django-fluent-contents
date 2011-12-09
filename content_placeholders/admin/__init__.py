from django.contrib import admin
from content_placeholders.admin.placeholdereditor import PlaceholderEditorAdminMixin, PlaceholderEditorAdmin, PlaceholderEditorInline
from content_placeholders.admin.placeholderfield import PlaceholderFieldAdmin, PlaceholderFieldAdminMixin
from content_placeholders.admin.contentitems import get_content_item_inlines

__all__ = (
    'PlaceholderEditorAdminMixin', 'PlaceholderEditorAdmin', 'PlaceholderEditorInline',
    'PlaceholderFieldAdmin', 'PlaceholderFieldAdminMixin',
    'get_content_item_inlines',
)


from content_placeholders.admin.debug import PlaceholderAdmin
from content_placeholders.models.db import Placeholder, ContentItem
admin.site.register(Placeholder, PlaceholderAdmin)
admin.site.register(ContentItem)
