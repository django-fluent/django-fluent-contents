from django.contrib import admin
from content_placeholders.admin.debug import PlaceholderAdmin
from content_placeholders.admin.placeholderfield import PlaceholderFieldAdmin, PlaceholderInline
from content_placeholders.admin.contentitems import ContentItemInline, get_content_item_inlines
from content_placeholders.models.db import Placeholder, ContentItem

__all__ = (
    'PlaceholderFieldAdmin', 'PlaceholderInline',  'ContentItemInline', 'get_content_item_inlines',
)

#admin.site.register(Placeholder, PlaceholderAdmin)
#admin.site.register(ContentItem)
