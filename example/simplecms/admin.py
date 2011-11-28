from django.contrib import admin
from django.utils.safestring import mark_safe
from mptt.admin import MPTTModelAdmin
from content_placeholders.admin.contentitems import get_content_item_inlines
from content_placeholders.admin.placeholderfield import PlaceholderInline
from simplecms.models import Page


class PageAdmin(MPTTModelAdmin):
    """
    Administration screen for pages
    """
    list_display = ('title', 'slug', 'cached_url')
    prepopulated_fields = { 'slug': ('title',), }

    def cached_url(self, page):
        return mark_safe('<a href="{0}">{1}</a>'.format(page.get_absolute_url(), page._cached_url))

    cached_url.allow_tags = True


    # This is where the magic happens
    inlines = [PlaceholderInline] + get_content_item_inlines()


admin.site.register(Page, PageAdmin)
