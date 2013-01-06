from django.contrib.admin.options import InlineModelAdmin
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
    def __init__(self, *args, **kwargs):
        super(BaseContentItemFormSet, self).__init__(*args, **kwargs)
        self._deleted_placeholders = ()  # internal property, set by PlaceholderEditorAdmin


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
        if commit:
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
                form.instance.placeholder = desired_placeholder

            elif form.instance.placeholder_id in self._deleted_placeholders:
                # ContentItem was in a deleted placeholder, and gets orphaned.
                form.cleaned_data['placeholder'] = None
                form.instance.placeholder = None


    @classmethod
    def get_default_prefix(cls):
        # Make output less verbose, easier to read, and less kB to transmit.
        opts = cls.model._meta
        return opts.object_name.lower()

    @property
    def type_name(self):
        """
        Return the classname of the model, this is mainly provided for templates.
        """
        return self.model.__name__


class ContentItemInlineMixin(InlineModelAdmin):
    """
    Base functionality for a ContentItem inline.
    This class can be mixed with a regular `InlineModelAdmin` or `GenericInlineModelAdmin`.
    """
    # inline settings
    extra = 0
    ordering = ('sort_order',)
    template = 'admin/fluent_contents/contentitem/inline_container.html'
    form = ContentItemForm
    is_fluent_editor_inline = True  # Allow admin templates to filter the inlines

    # overwritten by subtype
    name = None
    plugin = None
    extra_fieldsets = None
    type_name = None
    cp_admin_form_template = None
    cp_admin_init_template = None

    # Extra settings
    base_fields = ('placeholder', 'placeholder_slot', 'sort_order',)  # base fields in ContentItemForm


    def __init__(self, *args, **kwargs):
        super(ContentItemInlineMixin, self).__init__(*args, **kwargs)
        self.verbose_name_plural = u'---- ContentItem Inline: %s' % (self.verbose_name_plural,)


    @property
    def media(self):
        media = super(ContentItemInlineMixin, self).media
        if self.plugin:
            media += self.plugin.media  # form fields first, plugin afterwards
        return media


    def get_fieldsets(self, request, obj=None):
        # If subclass declares fieldsets, this is respected
        if not self.extra_fieldsets or self.declared_fieldsets:
            return super(ContentItemInlineMixin, self).get_fieldsets(request, obj)

        return ((None, {'fields': self.base_fields}),) + self.extra_fieldsets


    def formfield_for_dbfield(self, db_field, **kwargs):
        # Allow to use formfield_overrides using a fieldname too.
        # Avoids the major need to reroute formfield_for_dbfield() via the plugin.
        try:
            attrs = self.formfield_overrides[db_field.name]
            kwargs = dict(attrs, **kwargs)
        except KeyError:
            pass
        return super(ContentItemInlineMixin, self).formfield_for_dbfield(db_field, **kwargs)


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
    Dynamically generate genuine django inlines for all registered content item types.
    When the `plugins` parameter is ``None``, all plugin inlines are returned.
    """
    COPY_FIELDS = (
        'form', 'raw_id_fields', 'filter_vertical', 'filter_horizontal',
        'radio_fields', 'prepopulated_fields', 'formfield_overrides', 'readonly_fields',
    )
    if plugins is None:
        plugins = extensions.plugin_pool.get_plugins()

    inlines = []
    for plugin in plugins:  # self.model._supported_...()
        # Avoid errors that are hard to trace
        if not isinstance(plugin, extensions.ContentPlugin):
            raise TypeError("get_content_item_inlines() expects to receive ContentPlugin instances, not {0}".format(plugin))

        ContentItemType = plugin.model

        # Create a new Type that inherits CmsPageItemInline
        # Read the static fields of the ItemType to override default appearance.
        # This code is based on FeinCMS, (c) Simon Meers, BSD licensed
        name = '%s_AutoInline' %  ContentItemType.__name__
        attrs = {
            '__module__': plugin.__class__.__module__,
            'model': ContentItemType,

            # Add metadata properties for template
            'name': plugin.verbose_name,
            'plugin': plugin,
            'type_name': plugin.type_name,
            'extra_fieldsets': plugin.fieldsets,
            'cp_admin_form_template': plugin.admin_form_template,
            'cp_admin_init_template': plugin.admin_init_template,
        }

        # Copy a restricted set of admin fields to the inline model too.
        for name in COPY_FIELDS:
            if getattr(plugin, name):
                attrs[name] = getattr(plugin, name)

        inlines.append(type(name, (base,), attrs))

    # For consistency, enforce ordering
    inlines.sort(key=lambda inline: inline.name.lower())

    return inlines
