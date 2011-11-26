from django.contrib import admin
from content_placeholders.admin.contentitems import get_content_item_inlines
from content_placeholders import extensions


class PlaceholderAdmin(admin.ModelAdmin):
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


    # ---- Inline insertion ----

    def __init__(self, model, admin_site):
        super(PlaceholderAdmin, self).__init__(model, admin_site)
        self._initialized_inlines = False


    def get_form(self, request, obj=None, **kwargs):
        self._initialize_content_item_inlines()   # delayed the initialisation a bit
        return super(PlaceholderAdmin, self).get_form(request, obj, **kwargs)


    def _initialize_content_item_inlines(self):
        # Calling it too early places more stress on the Django load mechanisms.
        # e.g. load_middleware() -> import x.admin.something -> processes __init__.py ->
        #      admin.site.register(PlaceholderAdmin) -> PlaceholderAdmin::__init__() -> start looking for plugins -> ImportError
        if not self._initialized_inlines:
            for InlineType in get_content_item_inlines():
                inline_instance = InlineType(self.model, self.admin_site)
                self.inline_instances.append(inline_instance)

            self._initialized_inlines = True

