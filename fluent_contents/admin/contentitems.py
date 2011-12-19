from django.contrib.contenttypes.generic import BaseGenericInlineFormSet
from django.contrib.contenttypes.models import ContentType
from fluent_contents import extensions
from fluent_contents.admin.genericextensions import ExtensibleGenericInline
from fluent_contents.forms import ContentItemForm
from fluent_contents.models.db import Placeholder


class BaseContentItemFormSet(BaseGenericInlineFormSet):
    """
    Correctly save placeholder fields.
    """
    def save_new(self, form, commit=True):
        # This is the moment to link the form 'placeholder_slot' field to a placeholder..
        # Notice that the PlaceholderEditorInline needs to be included before any ContentItemInline,
        # so it creates the Placeholder just before the ContentItem models are saved.
        #
        # In Django 1.3:
        # The save_new() function does not call form.save(), but constructs the model itself.
        # This allows it to insert the parent relation (ct_field / ct_fk_field) since they don't exist in the form.
        # It then calls form.cleaned_data to get all values, and use Field.save_form_data() to store them in the model instance.
        self._set_placeholder_id(form)
        return super(BaseContentItemFormSet, self).save_new(form, commit=commit)


    def save_existing(self, form, instance, commit=True):
        self._set_placeholder_id(form)
        return form.save(commit=commit)


    def _set_placeholder_id(self, form):
        # If the slot is given, it overwrites whatever placeholder is selected.
        form_slot = form.cleaned_data['placeholder_slot']
        if form_slot:
            form_placeholder = form.cleaned_data['placeholder']   # could already be updated, or still point to previous placeholder.

            if not form_placeholder or form_placeholder.slot != form_slot:
                desired_placeholder = Placeholder.objects.get(
                    slot=form_slot,
                    parent_type=ContentType.objects.get_for_model(self.instance),
                    parent_id=self.instance.id
                )

                form.cleaned_data['placeholder'] = desired_placeholder



class ContentItemInlineMixin(object):
    """
    Base functionality for a ContentItem inline.
    This class can be mixed with a regular `InlineModelAdmin` or `GenericInlineModelAdmin`.
    """
    # inline settings
    extra = 0
    ordering = ('sort_order',)
    template = 'admin/fluent_contents/contentitem/inline_container.html'

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
