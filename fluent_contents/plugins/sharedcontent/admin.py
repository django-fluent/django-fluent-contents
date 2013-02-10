from django.contrib import admin
from fluent_contents.admin import PlaceholderFieldAdmin
from fluent_contents.plugins.sharedcontent.models import SharedContent


class SharedContentAdmin(PlaceholderFieldAdmin):
    """
    Admin screen for the shared content, displayed in the global Django admin.
    """
    list_display = ('title', 'slug')
    prepopulated_fields = {
        'slug': ('title',)
    }


admin.site.register(SharedContent, SharedContentAdmin)
