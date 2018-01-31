import django
from django.contrib.contenttypes.fields import GenericRelation, GenericRel
from django.contrib.contenttypes.models import ContentType
from django.db import DEFAULT_DB_ALIAS
from django.db.models.query_utils import Q
from django.utils.functional import lazy
from django.utils.text import capfirst
from fluent_contents import appsettings
from fluent_contents.forms.fields import PlaceholderFormField
from fluent_contents.models import Placeholder, ContentItem

__all__ = (
    'PlaceholderRelation', 'ContentItemRelation',
    'PlaceholderField',
)

# The PlaceholderField is inspired by Django CMS
# Yet uses a different methology to access the fields.
#
# In Django CMS it's a ForeignKey to Placeholder.
# Here, the Placeholder has a GenericForeignKey to the parent - hence it will be deleted when the parent is removed -
# so the PlaceholderField is merely a reverse GenericRelation.
#
# In the admin, the logic of the PlaceholderEditor code can be reused.


class PlaceholderRelation(GenericRelation):
    """
    A :class:`~django.contrib.contenttypes.generic.GenericRelation` which can be applied to a parent model that
    is expected to be referenced be a :class:`~fluent_contents.models.Placeholder`. For example:

    .. code-block:: python

        class Page(models.Model):
            placeholder_set = PlaceholderRelation()
    """

    def __init__(self, **kwargs):
        defaults = {
            'limit_choices_to': Q(
                parent_type=lazy(lambda: ContentType.objects.get_for_model(Placeholder), ContentType)()
            )
        }
        defaults.update(kwargs)
        super(PlaceholderRelation, self).__init__(to=Placeholder,
            object_id_field='parent_id', content_type_field='parent_type', **defaults)


class ContentItemRelation(GenericRelation):
    """
    A :class:`~django.contrib.contenttypes.generic.GenericRelation` which can be applied to a parent model that
    is expected to be referenced by the :class:`~fluent_contents.models.ContentItem` classes. For example:

    .. code-block:: python

        class Page(models.Model):
            contentitem_set = ContentItemRelation()

    Adding this relation also causes the admin delete page to list the
    :class:`~fluent_contents.models.ContentItem` objects which will be deleted.
    """

    def __init__(self, **kwargs):
        super(ContentItemRelation, self).__init__(to=ContentItem,
            object_id_field='parent_id', content_type_field='parent_type', **kwargs)

    def bulk_related_objects(self, objs, using=DEFAULT_DB_ALIAS):
        # Fix delete screen. Workaround for https://github.com/django-polymorphic/django-polymorphic/issues/34
        return super(ContentItemRelation, self).bulk_related_objects(objs).non_polymorphic()


class PlaceholderRel(GenericRel):
    """
    The internal :class:`~django.contrib.contenttypes.generic.GenericRel`
    that is used by the :class:`PlaceholderField` to support queries.
    """

    def __init__(self, field, to, related_name=None, related_query_name=None, limit_choices_to=None):
        # Note: all other args are provided for Django 1.9 compatibility
        limit_choices_to = Q(
            parent_type=lazy(lambda: ContentType.objects.get_for_model(Placeholder), ContentType)(),
            slot=field.slot,
        )

        # TODO: make sure reverse queries work properly
        super(PlaceholderRel, self).__init__(
            field=field,
            to=Placeholder,
            related_name=None,  # NOTE: must be unique for app/model/slot.
            limit_choices_to=limit_choices_to
        )


class PlaceholderFieldDescriptor(object):
    """
    This descriptor is placed on the PlaceholderField model instance
    by the :func:`~PlaceholderField.contribute_to_class` function.
    This causes ``instance.field`` to return a :class:`~fluent_contents.models.Placeholder` object.
    """

    def __init__(self, slot):
        """Set the slot this descriptor is created for."""
        self.slot = slot

    def __get__(self, instance, instance_type=None):
        """Return the placeholder by slot."""
        if instance is None:
            return self
        try:
            placeholder = Placeholder.objects.get_by_slot(instance, self.slot)
        except Placeholder.DoesNotExist:
            raise Placeholder.DoesNotExist("Placeholder does not exist for parent {0} (type_id: {1}, parent_id: {2}), slot: '{3}'".format(
                repr(instance),
                ContentType.objects.get_for_model(instance).pk,
                instance.pk,
                self.slot
            ))
        else:
            placeholder.parent = instance  # fill the reverse cache
            return placeholder

    def __set__(self, instance, value):
        if instance is None:
            raise AttributeError("Descriptor must be accessed via instance")

        if value == "-DUMMY-":
            return

        raise NotImplementedError("Setting Placeholder value is not supported, use Placeholder.objects.create_for_object() instead.")


class PlaceholderField(PlaceholderRelation):
    """
    The model field to add :class:`~fluent_contents.models.ContentItem` objects to a model.

    :param slot: A programmatic name to identify the placeholder.
    :param plugins: Optional, define which plugins are allowed to be used. This can be a list of names, or :class:`~fluent_contents.extensions.ContentPlugin` references.
    :type slot: str
    :type plugins: list

    This class provides the form fields for the field. Use this class in a model to use it:

    .. code-block:: python

        class Article(models.Model):
            contents = PlaceholderField("article_contents")

    The data itself is stored as reverse relation in the :class:`~fluent_contents.models.ContentItem` object.
    Hence, all contents will be cleaned up properly when the parent model is deleted.

    The placeholder will be displayed in the admin:

    .. image:: /images/admin/placeholderfieldadmin1.png
       :width: 770px
       :height: 562px
       :alt: django-fluent-contents placeholder field preview
    """
    rel_class = PlaceholderRel  # Django 1.9

    def __init__(self, slot, plugins=None, **kwargs):
        """
        Initialize the placeholder field.
        """
        self.slot = slot
        super(PlaceholderField, self).__init__(**kwargs)

        # See if a plugin configuration is defined in the settings
        self._slot_config = appsettings.FLUENT_CONTENTS_PLACEHOLDER_CONFIG.get(slot) or {}
        self._plugins = plugins or self._slot_config.get('plugins') or None

        # Overwrite some hardcoded defaults from the base class.
        self.editable = True
        self.blank = True                     # TODO: support blank: False to enforce adding at least one plugin.

    def formfield(self, **kwargs):
        """
        Returns a :class:`PlaceholderFormField` instance for this database Field.
        """
        defaults = {
            'label': capfirst(self.verbose_name),
            'help_text': self.help_text,
            'required': not self.blank,
        }
        defaults.update(kwargs)
        return PlaceholderFormField(slot=self.slot, plugins=self._plugins, **defaults)

    def contribute_to_class(self, cls, name, **kwargs):
        """
        Internal Django method to associate the field with the Model; it assigns the descriptor.
        """
        super(PlaceholderField, self).contribute_to_class(cls, name, **kwargs)

        # overwrites what instance.<colname> returns; give direct access to the placeholder
        setattr(cls, name, PlaceholderFieldDescriptor(self.slot))

        # Make placeholder fields easy to find
        # Can't assign this to cls._meta because that gets overwritten by every level of model inheritance.
        if not hasattr(cls, '_meta_placeholder_fields'):
            cls._meta_placeholder_fields = {}
        cls._meta_placeholder_fields[name] = self

        # Configure the revere relation if possible.
        # TODO: make sure reverse queries work properly
        if django.VERSION >= (1, 11):
            rel = self.remote_field
        else:
            rel = self.rel

        if rel.related_name is None:
            # Make unique for model (multiple models can use same slotnane)
            rel.related_name = '{app}_{model}_{slot}_FIXME'.format(
                app=cls._meta.app_label,
                model=cls._meta.object_name.lower(),
                slot=self.slot
            )

            # Remove attribute must exist for the delete page. Currently it's not actively used.
            # The regular ForeignKey assigns a ForeignRelatedObjectsDescriptor to it for example.
            # In this case, the PlaceholderRelation is already the reverse relation.
            # Being able to move forward from the Placeholder to the derived models does not have that much value.
            setattr(rel.to, self.rel.related_name, None)

    @property
    def plugins(self):
        """
        Get the set of plugins that this field may display.
        """
        from fluent_contents import extensions
        if self._plugins is None:
            return extensions.plugin_pool.get_plugins()
        else:
            try:
                return extensions.plugin_pool.get_plugins_by_name(*self._plugins)
            except extensions.PluginNotFound as e:
                raise extensions.PluginNotFound(str(e) + " Update the plugin list of '{0}.{1}' field or FLUENT_CONTENTS_PLACEHOLDER_CONFIG['{2}'] setting.".format(self.model._meta.object_name, self.name, self.slot))

    def value_from_object(self, obj):
        """
        Internal Django method, used to return the placeholder ID when exporting the model instance.
        """
        try:
            # not using self.attname, access the descriptor instead.
            placeholder = getattr(obj, self.name)
        except Placeholder.DoesNotExist:
            return None   # Still allow ModelForm / admin to open and create a new Placeholder if the table was truncated.

        return placeholder.id if placeholder else None  # Be consistent with other fields, like ForeignKey
