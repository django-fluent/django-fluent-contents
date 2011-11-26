from django.contrib.contenttypes.generic import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.query_utils import Q
from django.utils.text import capfirst
from content_placeholders.forms.fields import PlaceholderFormField
from content_placeholders.forms.widgets import PlaceholderPluginEditor
from content_placeholders.models.db import Placeholder

# PlaceholderField
# Inspired, and based upon Django CMS
# (c) Django CMS developers, BSD licensed.

class PlaceholderRelation(GenericRelation):
    """
    A ``GenericRelation`` which can be applied to a model that is freuently references by a ``Placeholder``.
    It makes it possible to reverse
    """
    def __init__(self, **kwargs):
        super(PlaceholderRelation, self).__init__(to=Placeholder,
            object_id_field='parent_id', content_type_field='parent_type', **kwargs)


class PlaceholderField2(PlaceholderRelation):
    def __init__(self, **kwargs):
        self.slot = kwargs.pop('slot', None)
        limit_choices_to = Q(slot=self.slot) if self.slot is not None else None
        super(PlaceholderField2, self).__init__(limit_choices_to=limit_choices_to, **kwargs)
        self.slot = slotname




class PlaceholderField(models.ForeignKey):
    """
    A Placeholder field, to add a placeholder with content plugins to a custom model.
    """
    def __init__(self, slotname, **kwargs):
        self.slotname = slotname
        kwargs.update({'null':True}) # always allow Null
        super(PlaceholderField, self).__init__(Placeholder, **kwargs)


    def formfield(self, **kwargs):
        """
        Returns a django.forms.Field instance for this database Field.
        """
        defaults = {
            'label': capfirst(self.verbose_name),
            'help_text': self.help_text
        }
        defaults.update(kwargs)

        widget = PlaceholderPluginEditor()
        widget.choices = []
        defaults['widget'] = widget    # Also overrides for admin
        return PlaceholderFormField(required=False, **defaults)


    def formfield_for_admin(self, request, **kwargs):
        return self.formfield(**kwargs)


    def _get_new_placeholder(self, parent):
        return Placeholder.objects.create(
            slot=self.slotname,
            parent_type=ContentType.objects.get_for_model(parent),
            parent_id=parent.id
        )


    def pre_save(self, model_instance, add):
        if not model_instance.pk:
            # TODO: self.attname?
            setattr(model_instance, self.name, self._get_new_placeholder(model_instance))
        return super(PlaceholderField, self).pre_save(model_instance, add)


    def save_form_data(self, instance, data):
        if not instance.pk:
            # Still need to pass the parent, but parent_id will be null.
            data = self._get_new_placeholder(instance)
        else:
            data = getattr(instance, self.name)
            if not isinstance(data, Placeholder):
                data = self._get_new_placeholder(instance)
            elif data and not data.parent_id:
                # Got placeholder before, but without storing ID.
                # Fix that, add the parent_id to the placeholder.
                data.parent_id = instance.pk
                data.parent_type = ContentType.objects.get_for_model(instance)
        super(PlaceholderField, self).save_form_data(instance, data)


    def south_field_triple(self):
        """Returns a suitable description of this field for South."""
        # We'll just introspect ourselves, since we inherit.
        from south.modelsinspector import introspector
        field_class = "django.db.models.fields.related.ForeignKey"
        args, kwargs = introspector(self)
        # That's our definition!
        return field_class, args, kwargs


    def contribute_to_class(self, cls, name):
        super(PlaceholderField, self).contribute_to_class(cls, name)

        if not hasattr(cls._meta, 'placeholder_field_names'):
            cls._meta.placeholder_field_names = []
        if not hasattr(cls._meta, 'placeholder_fields'):
            cls._meta.placeholder_fields = {}

        cls._meta.placeholder_field_names.append(name)
        cls._meta.placeholder_fields[self] = name
        self.model = cls
