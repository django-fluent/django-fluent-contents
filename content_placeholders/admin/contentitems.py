from django.contrib.admin.util import flatten_fieldsets
from django.contrib.contenttypes.generic import GenericStackedInline, generic_inlineformset_factory
from django.utils.functional import curry
from content_placeholders import extensions


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
            'form': plugin.admin_form or extensions.ContentItemForm,

            # Add metadata properties for template
            'name': plugin.verbose_name,
            'plugin': plugin,
            'type_name': plugin.type_name,
            'cp_admin_form_template': plugin.admin_form_template
        }

        inlines.append(type(name, base, attrs))
    return inlines


class ContentItemInline(GenericStackedInline):
    """
    Custom ``InlineModelAdmin`` subclass used for content types.
    """

    # inline settings
    extra = 0
    ct_field = "parent_type"
    ct_fk_field = "parent_id"
    ordering = ('sort_order',)
    template = 'admin/content_placeholders/contentitem/inline_container.html'

    # overwritten by subtype
    name = None
    plugin = None
    type_name = None
    cp_admin_form_template = None


    def __init__(self, *args, **kwargs):
        super(ContentItemInline, self).__init__(*args, **kwargs)
        self.verbose_name_plural = u'---- ContentItem Inline: %s' % (self.verbose_name_plural,)


    @property
    def media(self):
        media = super(ContentItemInline, self).media
        if self.plugin:
            media += self.plugin.media  # form fields first, plugin afterwards
        return media


    def get_formset(self, request, obj=None):
        # Have to overwrite the entire get_formset() method
        # because the GenericStackedInline.get_formset does not provide a 'kwargs' option.
        # This is needed to insert a 'exclude' line that fixes django-polymorphic.
        if self.declared_fieldsets:
            fields = flatten_fieldsets(self.declared_fieldsets)
        else:
            fields = None
        if self.exclude is None:
            exclude = []
        else:
            exclude = list(self.exclude)
        exclude.extend(self.get_readonly_fields(request, obj))
        exclude.append('contentitem_ptr')   # FIX for django-polymorphic
        defaults = {
            "ct_field": self.ct_field,
            "fk_field": self.ct_fk_field,
            "form": self.form,
            "formfield_callback": curry(self.formfield_for_dbfield, request=request),
            "formset": self.formset,
            "extra": self.extra,
            "can_delete": self.can_delete,
            "can_order": False,
            "fields": fields,
            "max_num": self.max_num,
            "exclude": exclude
        }
        return generic_inlineformset_factory(self.model, **defaults)