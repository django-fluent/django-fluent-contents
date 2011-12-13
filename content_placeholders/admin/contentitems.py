from django.contrib.contenttypes.generic import BaseGenericInlineFormSet
from django.contrib.contenttypes.models import ContentType
from content_placeholders import extensions
from content_placeholders.admin.genericextensions import ExtensibleGenericInline
from content_placeholders.forms import ContentItemForm
from content_placeholders.models.db import Placeholder


class BaseContentItemFormSet(BaseGenericInlineFormSet):
    """
    Correctly save placeholder fields.
    """
    def save_new(self, form, commit=True):
        # This is the time to link the form 'placeholder_slot' field to a placeholder that was just created before.
        # Hence, the PlaceholderEditorInline needs to be included before any ContentItemInline.
        self._set_placeholder_id(form)
        return super(BaseContentItemFormSet, self).save_new(form, commit=commit)


    def save_existing(self, form, instance, commit=True):
        self._set_placeholder_id(form)
        return form.save(commit=commit)


    def _set_placeholder_id(self, form):
        if form.cleaned_data['placeholder_slot'] and not form.cleaned_data['placeholder']:
            saved_placeholder = Placeholder.objects.get(
                slot=form.cleaned_data['placeholder_slot'],
                parent_type=ContentType.objects.get_for_model(self.instance),
                parent_id=self.instance.id
            )
            form.cleaned_data['placeholder'] = saved_placeholder



class ContentItemInlineMixin(object):
    """
    Base functionality for a ContentItem inline.
    This class can be mixed with a regular `InlineModelAdmin` or `GenericInlineModelAdmin`.
    """
    # inline settings
    extra = 0
    ordering = ('sort_order',)
    template = 'admin/content_placeholders/contentitem/inline_container.html'

    # overwritten by subtype
    name = None
    plugin = None
    type_name = None
    cp_admin_form_template = None


    def __init__(self, *args, **kwargs):
        super(ContentItemInlineMixin, self).__init__(*args, **kwargs)
        self.verbose_name_plural = u'---- ContentItem Inline: %s' % (self.verbose_name_plural,)


    @property
    def media(self):
        media = super(ContentItemInlineMixin, self).media
        if self.plugin:
            media += self.plugin.media  # form fields first, plugin afterwards
        return media


class GenericContentItemInline(ContentItemInlineMixin, ExtensibleGenericInline):
    """
    Custom ``InlineModelAdmin`` subclass used for content types.
    """
    ct_field = "parent_type"
    ct_fk_field = "parent_id"
    formset = BaseContentItemFormSet
    exclude_unchecked = ('contentitem_ptr',)    # Fix django-polymorphic



def get_content_item_inlines(plugins=None, base=GenericContentItemInline):
    """
    Dynamically generate genuine django inlines for all registered content types.
    """
    if plugins is None:
        plugins = extensions.plugin_pool.get_plugins()

    inlines = []
    for plugin in plugins:  # self.model._supported_...()
        ContentItemType = plugin.model

        # Create a new Type that inherits CmsPageItemInline
        # Read the static fields of the ItemType to override default appearance.
        # This code is based on FeinCMS, (c) Simon Meers, BSD licensed
        name = '%s_AutoInline' %  ContentItemType.__name__
        attrs = {
            '__module__': plugin.__class__.__module__,
            'model': ContentItemType,
            'form': plugin.admin_form or ContentItemForm,

            # Add metadata properties for template
            'name': plugin.verbose_name,
            'plugin': plugin,
            'type_name': plugin.type_name,
            'cp_admin_form_template': plugin.admin_form_template
        }

        inlines.append(type(name, (base,), attrs))
    return inlines
