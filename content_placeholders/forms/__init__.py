from django import forms
from content_placeholders.models.db import Placeholder


class ContentItemForm(forms.ModelForm):
    """
    The base form for custom :class:`ContentItem` types.
    """
    placeholder = forms.ModelChoiceField(widget=forms.HiddenInput(), required=False, queryset=Placeholder.objects.all())
    placeholder_slot = forms.CharField(widget=forms.HiddenInput(), required=False)
    sort_order = forms.IntegerField(widget=forms.HiddenInput(), initial=1)
