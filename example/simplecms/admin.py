import json

from django.contrib import admin
from django.http import HttpResponse
from django.template.loader import get_template
from django.urls import path
from django.utils.safestring import mark_safe
from mptt.admin import MPTTModelAdmin
from simplecms import appconfig
from simplecms.models import Page

from fluent_contents.admin import PlaceholderEditorAdmin
from fluent_contents.analyzer import get_template_placeholder_data


@admin.register(Page)
class PageAdmin(PlaceholderEditorAdmin, MPTTModelAdmin):
    """
    Administration screen for pages
    """

    # Some decoration for the list/edit changes
    # This is all quite standard stuff.

    list_display = ("title", "slug", "cached_url")
    prepopulated_fields = {"slug": ("title",)}

    def cached_url(self, page):
        return mark_safe(f'<a href="{page.get_absolute_url()}">{page._cached_url}</a>')


    # This is where the magic happens.
    # Tell the base class which tabs to create

    def get_placeholder_data(self, request, obj):
        template = self.get_page_template(obj)
        return get_template_placeholder_data(template)

    def get_page_template(self, obj):
        if not obj:
            # Add page. start with default
            return get_template(appconfig.SIMPLECMS_DEFAULT_TEMPLATE)
        else:
            # Change page, honor template of object.
            return get_template(obj.template_name or appconfig.SIMPLECMS_DEFAULT_TEMPLATE)

    # Allow template layout changes in the client,
    # showing more power of the JavaScript engine.

    change_form_template = "admin/simplecms/page/change_form.html"

    class Media:
        js = ("simplecms/admin/simplecms_layouts.js",)

    def get_urls(self):
        """
        Introduce more urls
        """
        urls = super().get_urls()
        my_urls = [path("get_layout/", self.admin_site.admin_view(self.get_layout_view))]
        return my_urls + urls

    def get_layout_view(self, request):
        """
        Return the metadata about a layout
        """
        template_name = request.GET["name"]

        # Check if template is allowed, avoid parsing random templates
        templates = dict(appconfig.SIMPLECMS_TEMPLATE_CHOICES)
        if template_name not in templates:
            jsondata = {"success": False, "error": "Template not found"}
            status = 404
        else:
            # Extract placeholders from the template, and pass to the client.
            template = get_template(template_name)
            placeholders = get_template_placeholder_data(template)

            jsondata = {"placeholders": [p.as_dict() for p in placeholders]}
            status = 200

        jsonstr = json.dumps(jsondata)
        return HttpResponse(jsonstr, content_type="application/json", status=status)


