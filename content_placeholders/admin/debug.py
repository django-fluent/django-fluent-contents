from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin
from content_placeholders.admin.genericextensions import DynamicInlinesAdminMixin
from content_placeholders.admin.contentitems import get_content_item_inlines, ContentItemInlineMixin
from content_placeholders import extensions


class ContentItemInline(ContentItemInlineMixin, InlineModelAdmin):
    # Using different inline base class,
    # so the inline is associated by 'placeholder', and not 'parent' object.
    fk_name = 'placeholder'
    exclude = ('contentitem_ptr',)    # Fix django-polymorphic



class PlaceholderAdmin(DynamicInlinesAdminMixin, admin.ModelAdmin):
    list_display = ('slot', 'title', 'parent',)

    # ---- Frontend support ----

    # These files need to be loaded before the other plugin code,
    # It makes plugin development easier, because plygins can assume everything is present,
    class Media:
        js = (
            'content_placeholders/admin/cp_admin.js',
            'content_placeholders/admin/cp_data.js',
            'content_placeholders/admin/cp_plugins.js',
        )
        css = {
            'screen': (
                'content_placeholders/admin/cp_admin.css',
            ),
        }


    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        """Include plugin meta information, in the context."""
        plugin_list = extensions.plugin_pool.get_plugins()
        context.update({
            'cp_plugin_list': plugin_list,
            'cp_placeholders': [obj] if obj else [],
        })

        # And go with standard stuff
        return super(PlaceholderAdmin, self).render_change_form(request, context, add, change, form_url, obj)


    def get_extra_inlines(self, obj=None):
        allowed_plugins = obj.get_allowed_plugins() if obj else None
        return get_content_item_inlines(allowed_plugins, base=ContentItemInline)
