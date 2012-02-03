from django.contrib.contenttypes.generic import GenericRelation, GenericRel
from django.contrib.contenttypes.models import ContentType
from django.db.models.query_utils import Q
from django.db.utils import DatabaseError
from django.utils.text import capfirst
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
        defaults = {}
        try:
            defaults['limit_choices_to'] = Q(
                parent_type=ContentType.objects.get_for_model(Placeholder)
            )
        except DatabaseError:
            pass   # skip at first syncdb

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
    """
    def __init__(self, **kwargs):
        super(ContentItemRelation, self).__init__(to=ContentItem,
            object_id_field='parent_id', content_type_field='parent_type', **kwargs)


class PlaceholderRel(GenericRel):
    """
    The internal :class:`~django.contrib.contenttypes.generic.GenericRel`
    that is used by the :class:`PlaceholderField` to support queries.
    """
    def __init__(self, slot):
        limit_choices_to=None
        try:
            limit_choices_to = Q(
                parent_type=ContentType.objects.get_for_model(Placeholder),
                slot=slot,
            )
        except DatabaseError:
            pass   # skip at first syncdb

        # TODO: make sure reverse queries work properly
        super(PlaceholderRel, self).__init__(
            to=Placeholder,
            related_name='placeholderfield_{0}+'.format(slot),   # TODO: make unique for model (multiple models can use same slotnane)
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
        return Placeholder.objects.get_by_slot(instance, self.slot)


    def __set__(self, instance, value):
        if instance is None:
            raise AttributeError("Descriptor must be accessed via instance")

        if value == "-DUMMY-":
            return

        raise NotImplementedError("Setting Placeholder value is not supported, use Placeholder.objects.create_for_parent() instead.")


class PlaceholderField(PlaceholderRelation):
    """
    The model field to add :class:`~fluent_contents.models.ContentItem` objects to a model.
    This class provides the form fields for the field. Use this class in a model to use it:

    .. code-block:: python

        class Article(models.Model):
            contents = PlaceholderField("article_contents")

    The :attr:`slot` parameter is mandatory to identify the placeholder.
    The :attr:`plugins` can be optionally defined to limit which plugins are allowed to be used.
    The data itself is stored as reverse relation in the :class:`~fluent_contents.models.ContentItem` object.
    Hence, all contents will be cleaned up properly when the parent model is deleted.
    """
    def __init__(self, slot, plugins=None, **kwargs):
        """
        Initialize the placeholder field.
        """
        super(PlaceholderField, self).__init__(**kwargs)

        self.slot = slot
        self.plugins = plugins

        # Overwrite some hardcoded defaults from the base class.
        self.editable = True
        self.blank = True                     # TODO: support blank: False to enforce adding at least one plugin.
        self.rel = PlaceholderRel(self.slot)  # This support queries


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
        return PlaceholderFormField(slot=self.slot, plugins=self.plugins, **defaults)


    def contribute_to_class(self, cls, name):
        """
        Internal Django method to associate the field with the Model; it assigns the descriptor.
        """
        super(PlaceholderField, self).contribute_to_class(cls, name)

        # overwrites what instance.<colname> returns; give direct access to the placeholder
        setattr(cls, name, PlaceholderFieldDescriptor(self.slot))

        # Make placeholder fields easy to find
        if not hasattr(cls._meta, 'placeholder_fields'):
            cls._meta.placeholder_fields = {}
        cls._meta.placeholder_fields[name] = self


    def value_from_object(self, obj):
        """
        Internal Django method, used to return the placeholder ID when exporting the model instance.
        """
        placeholder = getattr(obj, self.name)           # not using self.attname, access the descriptor instead.
        return placeholder.id if placeholder else None  # Be consistent with other fields, like ForeignKey



try:
    from south.modelsinspector import add_ignored_fields
except ImportError:
    pass
else:
    # South 0.7.x ignores GenericRelation fields but doesn't ignore subclasses.
    # Taking the same fix as applied in http://south.aeracode.org/ticket/414
    _name_re = "^" + __name__.replace(".", "\.")
    add_ignored_fields((
        _name_re + "\.PlaceholderRelation",
        _name_re + "\.ContentItemRelation",
    ))
