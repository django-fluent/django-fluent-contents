from django import forms
from content_placeholders.forms.widgets import PlaceholderPluginEditor

class PlaceholderFormField(forms.Field):
    """
    A tagging interface to detect a placeholder field.
    """
    widget = PlaceholderPluginEditor

