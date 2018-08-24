from collections import deque

from django.utils.functional import cached_property
from django.utils.lru_cache import lru_cache
from fluent_utils.softdeps.any_urlfield import AnyUrlField
from polymorphic.admin import GenericStackedPolymorphicInline
from polymorphic.formsets import BaseGenericPolymorphicInlineFormSet
from polymorphic_tree.admin import PolymorphicMPTTChildModelAdmin, PolymorphicMPTTParentModelAdmin

from fluent_contents import appsettings, extensions
from fluent_contents.extensions import plugin_pool
from fluent_contents.forms import ContentItemForm
from fluent_contents.models import ContentItem, Placeholder, get_parent_language_code
from fluent_contents.rendering.utils import add_media

# base fields in ContentItemForm
BASE_FIELDS = (
    'polymorphic_ctype',  # Added by BasePolymorphicModelFormSet
    'placeholder',
    'placeholder_slot',
    'parent_item',
    'parent_item_uid',
    'sort_order',
    'item_uid',
)


class BaseContentItemFormSet(BaseGenericPolymorphicInlineFormSet):
    """
    Correctly save placeholder fields.
    """
    do_not_call_in_templates = True

    def __init__(self, *args, **kwargs):
        instance = kwargs['instance']
        if instance:
            self.current_language = get_parent_language_code(instance)
            if self.current_language and 'queryset' in kwargs:
                kwargs['queryset'] = kwargs['queryset'].filter(language_code=self.current_language)
        else:
            self.current_language = appsettings.FLUENT_CONTENTS_DEFAULT_LANGUAGE_CODE

        super(BaseContentItemFormSet, self).__init__(*args, **kwargs)
        self._deleted_placeholders = ()  # internal property, set by PlaceholderEditorAdmin
        self._placeholders_by_slot = {}

        self._current_placeholders = Placeholder.objects.parent(self.instance).in_bulk()

    @cached_property
    def forms(self):
        forms = super(BaseContentItemFormSet, self).forms
        instances = [form.instance for form in forms if form.instance.pk]
        self._prefetch_relations(instances)
        return forms

    def _prefetch_relations(self, instances):
        """
        Make sure the displayed related objects are fetched in a single call.
        This avoids having many N-queries for related data in the formset.
        """
        # Allow django-any-urlfield 2.6 to resolve it's data.
        if hasattr(AnyUrlField, 'resolve_objects'):
            AnyUrlField.resolve_objects(instances)

    def get_form_class(self, model):
        form = super(BaseContentItemFormSet, self).get_form_class(model)
        # Make sure that the automatically generated form does have all our common fields first.
        # This allows the admin CSS to pick .form-row:last-child

        # Redefine field order
        first_fields = list(ContentItemForm.base_fields.keys())
        field_order = first_fields + [f for f in form.base_fields.keys() if f not in first_fields]

        # Can't update collections.OrderedDict.__root easily, so recreate the object.
        base_fields = form.base_fields
        form.base_fields = base_fields.__class__((k, base_fields[k]) for k in field_order)
        return form

    def _construct_form(self, i, **kwargs):
        form = super(BaseContentItemFormSet, self)._construct_form(i, **kwargs)
        self.fill_caches(form)
        return form

    def fill_caches(self, form):
        """
        Optimize the formset processing, by sharing objects between different forms.
        This is a workaround for the
        """
        contentitems = getattr(self, '_object_dict', None)
        form.fill_caches(placeholders=self._current_placeholders, contentitems=contentitems)

    def set_deleted_placeholders(self, deleted_placeholders):
        """
        Internal feature - make this formset aware of deleted placeholders.
        This makes sure ContentItems are not assigned to a Placeholder that is about to be deleted.
        (which would cause a cascade delete of the content too).
        """
        self._deleted_placeholders = deleted_placeholders

    def save(self, commit=True):
        # Trouble in paradise: the objects can't be saved directly,
        # as their saving order depends on the parents being saved first.
        changed_objects = super(BaseContentItemFormSet, self).save(commit=False)
        changed_objects = self._order_by_parent(changed_objects)

        if commit:
            for contentitem in changed_objects:
                contentitem.save()
            for contentitem in self.deleted_objects:
                self.delete_existing(contentitem)
            self.save_m2m()
        return changed_objects

    def _order_by_parent(self, contentitems):
        """
        Order the list of items by their parent.
        This uses the temporary ``_item_uid`` fields that _save_uuid_fields() added.
        """
        item_by_uuid = {item._item_uid: item for item in contentitems if item._item_uid}
        queue = deque(contentitems)
        seen = set()  # fast 'in' lookup
        result = []
        loops = 0

        while queue:
            # Avoid recursion over incomplete parent/child relationships.
            loops += 1
            if loops > len(queue):
                raise RuntimeError("Unable to restore tree structure of new items: {}".format(
                    ", ".join("<ContentItem {} (uid {}) -> parent {}>".format(
                        item.pk, item._item_uid, item._parent_item_uid
                    ) for item in queue)
                ))

            item = queue.popleft()
            if not item._parent_item_uid or item._parent_item_uid in seen:
                # Place in result list
                result.append(item)
                seen.add(item._item_uid)
                loops = 0

                # Relink to the parent since both are known now.
                if not item.parent_item_id and item._parent_item_uid:
                    item.parent = item_by_uuid[item._parent_item_uid]
            else:
                queue.append(item)

        return result

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
        self._save_uuid_fields(form)

        # As save_new() completely circumvents form.save(), have to insert the language code here.
        instance = super(BaseContentItemFormSet, self).save_new(form, commit=False)
        instance.language_code = self.current_language

        if commit:
            instance.save()
            form.save_m2m()

        return instance

    def save_existing(self, form, instance, commit=True):
        if commit:
            self._set_placeholder_id(form)
        self._save_uuid_fields(form)
        return form.save(commit=commit)

    def _set_placeholder_id(self, form):
        # If the slot is given, it overwrites whatever placeholder is selected.
        form_slot = form.cleaned_data['placeholder_slot']
        if form_slot:
            form_placeholder = form.cleaned_data['placeholder']   # could already be updated, or still point to previous placeholder.

            if not form_placeholder or form_placeholder.slot != form_slot:
                # Fetch the placeholder if needed, avoid having to repeat that query.
                try:
                    desired_placeholder = self._placeholders_by_slot[form_slot]
                except KeyError:
                    desired_placeholder = Placeholder.objects.parent(self.instance).get(slot=form_slot)
                    self._placeholders_by_slot[form_slot] = desired_placeholder

                form.cleaned_data['placeholder'] = desired_placeholder
                form.instance.placeholder = desired_placeholder

            elif form.instance.placeholder_id in self._deleted_placeholders:
                # ContentItem was in a deleted placeholder, and gets orphaned.
                form.cleaned_data['placeholder'] = None
                form.instance.placeholder = None

    def _save_uuid_fields(self, form):
        # Make sure the uuid fields are temporary stored
        # so they can be linked once all objects are constructed.
        form.instance._item_uid = form.cleaned_data.get('item_uid', None)
        form.instance._parent_item_uid = form.cleaned_data.get('parent_item_uid', None)

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
        #raise NotImplementedError()
        return self.model.__name__


class BaseContentItemAdminOptions(object):
    # Default admin settings
    form = ContentItemForm

    # overwritten by create_inline_for_plugin()
    name = None
    plugin = None
    extra_fieldsets = None
    type_name = None
    cp_admin_form_template = None
    cp_admin_init_template = None

    @property
    def media(self):
        media = super(BaseContentItemAdminOptions, self).media
        if self.plugin:
            media += self.plugin.media  # form fields first, plugin afterwards
        return media

    def get_fieldsets(self, request, obj=None):
        if not self.extra_fieldsets:
            # Let the admin auto detection do it's job. (means reading the form or formset class)
            return super(BaseContentItemAdminOptions, self).get_fieldsets(request, obj)
        else:
            return ((None, {'fields': BASE_FIELDS}),) + self.extra_fieldsets

    def formfield_for_dbfield(self, db_field, **kwargs):
        # Allow to use formfield_overrides using a fieldname too.
        # Avoids the major need to reroute formfield_for_dbfield() via the plugin.
        try:
            attrs = self.formfield_overrides[db_field.name]
            kwargs = dict(attrs, **kwargs)
        except KeyError:
            pass
        return super(BaseContentItemAdminOptions, self).formfield_for_dbfield(db_field, **kwargs)


class BaseContentItemInline(GenericStackedPolymorphicInline):
    """
    The ``InlineModelAdmin`` class used for all content items.
    """
    # inline settings
    ct_field = "parent_type"
    ct_fk_field = "parent_id"
    formset = BaseContentItemFormSet
    exclude = ('contentitem_ptr',)    # Fix django-polymorphic
    extra = 0  # defined on each child.
    ordering = ('sort_order',)
    template = 'admin/fluent_contents/contentitem/inline_container.html'
    is_fluent_editor_inline = True  # Allow admin templates to filter the inlines

    # Defined via get_content_item_inlines()
    plugins = []

    def __init__(self, parent_model, admin_site):
        super(BaseContentItemInline, self).__init__(parent_model, admin_site)
        self.verbose_name_plural = u'---- ContentItem Inline: %s' % (self.verbose_name_plural,)

    @property
    def media(self):
        # All admin media (e.g. for filter_horizontal)
        media = super(BaseContentItemInline, self).media

        # Plugin media is included afterwards
        for plugin in self.plugins:
            add_media(media, plugin.media)

        return media

    class Child(BaseContentItemAdminOptions, GenericStackedPolymorphicInline.Child):
        """
        The inline for each child model.
        Most settings are placed here by the :func:`create_inline_for_plugin` function.
        """
        media = BaseContentItemAdminOptions.media  # optimize MediaDefiningClass
        exclude = ('contentitem_ptr',)  # Fix django-polymorphic

        # for completeness, because parent admin handles it all.
        ct_field = "parent_type"
        ct_fk_field = "parent_id"


def get_content_item_inlines(plugins=None, parent_base=BaseContentItemInline, child_base=None):
    """
    Dynamically generate genuine django inlines for all registered content item types.
    When the `plugins` parameter is ``None``, all plugin inlines are returned.
    """
    if plugins is None:
        plugins = extensions.plugin_pool.get_plugins()
    if child_base is None:
        child_base = parent_base.Child

    child_inlines = []
    for plugin in plugins:
        child_inlines.append(
            create_inline_for_plugin(plugin, base=child_base)
        )

    # Construct a subclass of the Inline class,
    # that is configured with the static settings provided here.
    # Nowadays just one, that can spawn different form types.
    return [
        type('ContentItemParentInline', (parent_base,), {
            'model': ContentItem,
            'plugins': plugins,
            'child_inlines': child_inlines,
        })
    ]


def get_content_item_admin_options(plugin):
    """
    Get the settings for the Django admin class
    """
    # Avoid errors that are hard to trace
    if not isinstance(plugin, extensions.ContentPlugin):
        raise TypeError("get_content_item_inlines() expects to receive ContentPlugin instances, not {0}".format(plugin))

    COPY_FIELDS = (
        'form', 'raw_id_fields', 'filter_vertical', 'filter_horizontal',
        'radio_fields', 'prepopulated_fields', 'formfield_overrides', 'readonly_fields',
    )

    attrs = {
        '__module__': plugin.__class__.__module__,
        'model': plugin.model,

        # Add metadata properties for BaseContentItemAdminOptions and the template
        'name': plugin.verbose_name,
        'plugin': plugin,
        'type_name': plugin.type_name,
        'cp_admin_form_template': plugin.admin_form_template,
        'cp_admin_init_template': plugin.admin_init_template,
        'extra_fieldsets': tuple(plugin.fieldsets) if plugin.fieldsets else tuple(),
    }

    # Copy a restricted set of admin fields to the inline model too.
    for name in COPY_FIELDS:
        if getattr(plugin, name):
            attrs[name] = getattr(plugin, name)
    return attrs


@lru_cache()
def create_inline_for_plugin(plugin, base=BaseContentItemInline.Child):
    """
    Create the admin inline for a ContentItem plugin.
    """
    attrs = get_content_item_admin_options(plugin)
    class_name = '%s_AutoChildInline' % plugin.model.__name__
    return type(class_name, (base,), attrs)


class ContentItemParentAdmin(PolymorphicMPTTParentModelAdmin):
    """
    Base admin to show a single ContentItem
    """
    base_model = ContentItem

    def get_child_models(self):
        results = []
        for plugin in plugin_pool.get_plugins():
            child_admin = create_admin_for_plugin(plugin)
            results.append((plugin.model, child_admin))
        return results


class ContentItemChildAdmin(BaseContentItemAdminOptions, PolymorphicMPTTChildModelAdmin):
    """
    Base admin to show a single ContentItem
    """
    base_model = ContentItem
    base_form = ContentItemForm
    media = BaseContentItemAdminOptions.media  # optimize MediaDefiningClass


@lru_cache()
def create_admin_for_plugin(plugin, base=ContentItemChildAdmin):
    """
    Create the admin instance for a ContentItem plugin.
    """
    attrs = get_content_item_admin_options(plugin)
    #attrs['base_form'] = attrs['form']
    class_name = '%s_ChildAdmin' % plugin.model.__name__
    return type(class_name, (base,), attrs)
