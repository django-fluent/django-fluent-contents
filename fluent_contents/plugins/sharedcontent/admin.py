from django.contrib import admin
from fluent_contents.admin import PlaceholderFieldAdmin
from fluent_contents.plugins.sharedcontent.models import SharedContent


class SharedContentAdmin(PlaceholderFieldAdmin):
    """
    Admin screen for the shared content, displayed in the global Django admin.
    """
    list_display = ('title', 'slug')

    def get_prepopulated_fields(self, request, obj=None):
        # Needed instead of prepopulated_fields=.. for django-parler==0.9
        return {
            'slug': ('title',)
        }

    # Using declared_fieldsets for Django 1.4, otherwise fieldsets= would work too.
    declared_fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'contents')
        }),
    )

admin.site.register(SharedContent, SharedContentAdmin)
