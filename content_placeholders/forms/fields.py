from django import forms
from content_placeholders.forms.widgets import PlaceholderFieldWidget

class PlaceholderFormField(forms.Field):
    """
    A form field to display a placeholder field.
    """
    def __init__(self, slot, plugins=None, **kwargs):
        # Pass along...
        self.slot = slot
        self.plugins = plugins

        defaults = {
            'widget': PlaceholderFieldWidget(slot=slot, plugins=plugins),
        }
        defaults.update(kwargs)
        super(PlaceholderFormField, self).__init__(**defaults)
