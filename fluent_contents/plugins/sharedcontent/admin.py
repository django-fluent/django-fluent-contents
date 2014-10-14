from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from parler.admin import TranslatableAdmin
from fluent_contents import appsettings
from fluent_contents.admin import PlaceholderFieldAdmin
from fluent_utils.dry.admin import MultiSiteAdminMixin
from .models import SharedContent
from . import appsettings as sharedcontent_appsettings


class SharedContentAdmin(MultiSiteAdminMixin, TranslatableAdmin, PlaceholderFieldAdmin):
    """
    Admin screen for the shared content, displayed in the global Django admin.
    """
    filter_site = appsettings.FLUENT_CONTENTS_FILTER_SITE_ID
    list_display = ('title', 'slug')
    ordering = ('slug',)

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

    if sharedcontent_appsettings.FLUENT_SHARED_CONTENT_ENABLE_CROSS_SITE:
        declared_fieldsets[1][1]['fields'] += ('is_cross_site',)


admin.site.register(SharedContent, SharedContentAdmin)
