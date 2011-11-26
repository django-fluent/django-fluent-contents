from django.contrib import admin
from django.contrib.contenttypes.generic import GenericInlineModelAdmin
from content_placeholders import extensions
from content_placeholders.models import Placeholder
from content_placeholders.models.fields import PlaceholderField


class PlaceholderInline(GenericInlineModelAdmin):
    model = Placeholder
    ct_field = 'parent_type'
    ct_fk_field = 'parent_id'
    template = "admin/content_placeholders/placeholder/inline_tabs.html"
    extra = 0

    class Media:
        # cp_tabs.js is included here, as it's a presentation choice
        # to display the placeholder panes in a tabbar format.
        # The remaining scripts should just operate the same without it.
        js = ('content_placeholders/admin/cp_tabs.js',)
        extend = False   # No need for the standard 'admin/js/inlines.min.js' here.

    def get_all_allowed_plugins(self):
        """
        Return all plugin categories which can be used by placeholder content.
        """
        return extensions.plugin_pool.get_plugins()


class PlaceholderFieldAdmin(admin.ModelAdmin):
    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Render the ``PlaceholderField`` with the proper form widget.
        Avoid getting the '+' sign to add a new field.
        """
        if isinstance(db_field, PlaceholderField):
            return db_field.formfield_for_admin(**kwargs)
        return super(PlaceholderFieldAdmin, self).formfield_for_dbfield(db_field, **kwargs)



