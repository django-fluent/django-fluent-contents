from django.contrib import admin
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from mptt.admin import MPTTModelAdmin
from content_placeholders.admin.placeholderfield import PlaceholderEditorAdminMixin
from content_placeholders.analyzer import get_template_placeholder_data
from simplecms.models import Page


class PageAdmin(PlaceholderEditorAdminMixin, MPTTModelAdmin):
    """
    Administration screen for pages
    """
    list_display = ('title', 'slug', 'cached_url')
    prepopulated_fields = { 'slug': ('title',), }

    def cached_url(self, page):
        return mark_safe('<a href="{0}">{1}</a>'.format(page.get_absolute_url(), page._cached_url))

    cached_url.allow_tags = True


    # This is where the magic happens:

    def get_placeholder_data(self, request, obj):
        template = self.get_page_template(obj)
        return get_template_placeholder_data(template)


    def get_page_template(self, obj):
        if not obj:
            # Add page. start with default
            return get_template("theme1/pages/standard.html")
        else:
            # Change page, honor template of object.
            return get_template(obj.template_name)


admin.site.register(Page, PageAdmin)
