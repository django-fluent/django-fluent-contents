from django.contrib import admin
from content_placeholders.admin.debug import PlaceholderAdmin
from content_placeholders.admin.placeholderfield import PlaceholderFieldAdmin, PlaceholderFieldAdminMixin, PlaceholderInline
from content_placeholders.admin.contentitems import GenericContentItemInline, get_content_item_inlines

__all__ = (
    'PlaceholderFieldAdmin', 'PlaceholderFieldAdminMixin', 'PlaceholderInline', 'GenericContentItemInline', 'get_content_item_inlines',
)

#from content_placeholders.models.db import Placeholder, ContentItem
#admin.site.register(Placeholder, PlaceholderAdmin)
#admin.site.register(ContentItem)
