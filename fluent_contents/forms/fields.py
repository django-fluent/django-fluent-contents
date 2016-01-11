from django import forms
from fluent_contents.forms.widgets import PlaceholderFieldWidget


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
