from django import forms
from django.utils import six
from fluent_contents.forms.widgets import PlaceholderFieldWidget

if six.PY3:
    long = int


class PlaceholderFormField(forms.Field):
    """
    The internal form field to display a placeholder field.
    It displays the :class:`~fluent_dashboard.forms.PlaceholderFieldWidget`.
    """

    def __init__(self, slot, plugins=None, parent_object=None, **kwargs):
        # Pass along...
        self.slot = slot
        self._plugins = plugins

        defaults = {
            'widget': PlaceholderFieldWidget(
                slot=slot, plugins=plugins, parent_object=parent_object),
        }
        defaults.update(kwargs)
        super(PlaceholderFormField, self).__init__(**defaults)


class OptimizableModelChoiceField(forms.ModelChoiceField):
    """
    An optimized model choice field.
    This allows object reuse between a large group of forms in a formset.
    """

    def __init__(self, *args, **kwargs):
        self.object_map = kwargs.pop('object_map', {})
        super(OptimizableModelChoiceField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if value is None:
            return None
        try:
            # Instead of performing a queryset.get() for every form,
            # allow the models to have a shared cache of fields.
            return self.object_map[long(value)]
        except (KeyError, ValueError):
            return super(OptimizableModelChoiceField, self).to_python(value)

    def fill_cache(self, object_map):
        """
        Assign a set of known objects to this field.
        This makes sure the object doesn't have to be retrieved again during form validation.
        """
        self.object_map = object_map or {}

        if object_map:
            first_value = six.next(six.itervalues(object_map))
            if not isinstance(first_value, self.queryset.model):
                raise TypeError("Invalid cache type for OptimizableModelChoiceField, expected {0} got {1}".format(
                    self.queryset.model.__name__, first_value.__class__.__name__
                ))
