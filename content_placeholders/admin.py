from django.contrib import admin
from content_placeholders import extensions
from content_placeholders.models import Placeholder, ContentItem


def get_content_item_inlines():
    """
    Dynamically generate genuine django inlines for registered content types.
    """
    inlines = []
    for plugin in extensions.plugin_pool.get_plugins():  # self.model._supported_...()
        ContentItemType = plugin.model

        # Create a new Type that inherits CmsPageItemInline
        # Read the static fields of the ItemType to override default appearance.
        # This code is based on FeinCMS, (c) Simon Meers, BSD licensed
        base = (ContentItemInline,)
        name = '%s_AutoInline' %  ContentItemType.__name__
        attrs = {
            '__module__': plugin.__class__.__module__,
            'model': ContentItemType,
            'type_name': plugin.type_name,
            'form': plugin.admin_form or extensions.ContentItemForm,
            'name': plugin.verbose_name,
            'plugin': plugin,
            'cp_admin_form_template': plugin.admin_form_template
        }

        inlines.append(type(name, base, attrs))
    return inlines


class ContentItemInline(admin.StackedInline):
    """
    Custom ``InlineModelAdmin`` subclass used for content types.
    """

    # inline settings
    extra = 0
    fk_name = 'placeholder'
    template = 'admin/content_placeholders/placeholder/inline_container.html'
    ordering = ('sort_order',)

    # overwritten by subtype
    name = None
    plugin = None
    type_name = None
    ecms_admin_form_template = None


    def __init__(self, *args, **kwargs):
        super(ContentItemInline, self).__init__(*args, **kwargs)
        self.verbose_name_plural = u'---- ContentItem Inline: %s' % (self.verbose_name_plural,)

    @property
    def media(self):
        media = super(ContentItemInline, self).media
        if self.plugin:
            media += self.plugin.media  # form fields first, plugin afterwards
        return media


class PlaceholderAdmin(admin.ModelAdmin):

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
        categories = extensions.plugin_pool.get_plugin_categories()
        categories_list = categories.items()
        categories_list.sort(key=lambda item: item[0])
        context.update({
            'cp_plugin_categories': categories_list,
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


admin.site.register(Placeholder, PlaceholderAdmin)
