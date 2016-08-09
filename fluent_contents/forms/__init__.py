from django import forms
from polymorphic_tree.admin import PolymorpicMPTTAdminForm

from fluent_contents.models import Placeholder, ContentItem
from .fields import OptimizableModelChoiceField

__all__ = ('ContentItemForm',)


class ContentItemForm(PolymorpicMPTTAdminForm):
    """
    The base form for custom :class:`~fluent_contents.models.ContentItem` types.
    It displays the additional meta fields as hidden fields.

    When creating custom admin forms (e.g. to add validation for specific fields),
    use this class as base to ensure all fields are properly set up.
    """
    polymorphic_ctype = forms.ChoiceField(widget=forms.HiddenInput(), required=True)  # redefined by formset
    placeholder = OptimizableModelChoiceField(widget=forms.HiddenInput(), required=False, queryset=Placeholder.objects.all())
    parent_item = OptimizableModelChoiceField(widget=forms.HiddenInput(), required=False, queryset=ContentItem.objects.none())
    parent_item_uid = forms.CharField(widget=forms.HiddenInput(), required=False)  # to link items before saving
    sort_order = forms.IntegerField(widget=forms.HiddenInput(), initial=1)

    # The placeholder_slot is an extra field that does not exist in the model.
    # When a page is created, the placeholder_id cannot be filled in yet.
    # Instead, the frontend fills in the placeholder_slot, and the BaseContentItemFormSet
    # will link the placeholder_id afterwards when the placeholder was also created.
    placeholder_slot = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super(ContentItemForm, self).__init__(*args, **kwargs)
        if self.instance.parent_id:
            # Not limited to placeholder, as the group can change during save.
            self.fields['parent_item'].queryset = ContentItem.objects.can_have_children().filter(
                parent_type=self.instance.parent_type_id,
                parent_id=self.instance.parent_id,
            ).exclude_descendants(self.instance, include_self=True)
            self.initial['parent_item_uid'] = self.instance.parent_id
        #else:
        #    self.fields['parent_item'].queryset = ContentItem.objects.can_have_children()

    def fill_caches(self, placeholders, contentitems):
        """
        Internal feature - Make the form aware of related objects.
        This optimizes the ``ModelChoiceField``, which is otherwise fetched again for every form.
        """
        self.fields['placeholder'].fill_cache(placeholders)
        self.fields['parent_item'].fill_cache(contentitems)

    def save(self, commit=True):
        self.instance.clear_cache()   # Make sure the cache is cleared. No matter what instance.save() does.
        return super(ContentItemForm, self).save(commit)
