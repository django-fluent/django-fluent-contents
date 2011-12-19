from django import forms
from fluent_contents.models.db import Placeholder


class ContentItemForm(forms.ModelForm):
    """
    The base form for custom :class:`ContentItem` types.
    """
    placeholder = forms.ModelChoiceField(widget=forms.HiddenInput(), required=False, queryset=Placeholder.objects.all())
    sort_order = forms.IntegerField(widget=forms.HiddenInput(), initial=1)

    # The placeholder_slot is an extra field that does not exist in the model.
    # When a page is created, the placeholder_id cannot be filled in yet.
    # Instead, the frontend fills in the placeholder_slot, and the BaseContentItemFormSet
    # will link the placeholder_id afterwards when the placeholder was also created.
    placeholder_slot = forms.CharField(widget=forms.HiddenInput(), required=False)
