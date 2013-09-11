from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from parler.admin import TranslatableAdmin
from fluent_contents.admin import PlaceholderFieldAdmin
from fluent_contents.plugins.sharedcontent.models import SharedContent


class SharedContentAdmin(TranslatableAdmin, PlaceholderFieldAdmin):
    """
    Admin screen for the shared content, displayed in the global Django admin.
    """
    list_display = ('title', 'slug')

    def get_prepopulated_fields(self, request, obj=None):
        # Needed instead of prepopulated_fields=.. for django-parler==0.9
        if obj is not None and obj.pk:
            # Avoid overwriting the slug when adding a new language.
            return {}
        else:
            return {
                'slug': ('title',)
            }

    # Using declared_fieldsets for Django 1.4, otherwise fieldsets= would work too.
    declared_fieldsets = (
        (None, {
            'fields': ('title', 'contents')
        }),
        (_("Publication settings"), {
            'fields': ('slug',),
            'classes': ('collapse',),
        })
    )

admin.site.register(SharedContent, SharedContentAdmin)
