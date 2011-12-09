from django.contrib.admin.util import flatten_fieldsets
from django.contrib.contenttypes.generic import GenericInlineModelAdmin, generic_inlineformset_factory
from django.utils.functional import curry


class ExtensibleGenericInline(GenericInlineModelAdmin):
    """
    Custom ``GenericStackedInline`` subclass that got some of it's extensibility back.
    """
    exclude_unchecked = None

    def get_formset(self, request, obj=None, **kwargs):
        """
        Overwritten ``GenericStackedInline.get_formset`` to restore two options:
        - Add a ``exclude_unchecked`` field, that allows adding fields like the ``_ptr`` fields.
        - Restore the ``kwargs`` option.
        """
        if self.declared_fieldsets:
            fields = flatten_fieldsets(self.declared_fieldsets)
        else:
            fields = None
        if self.exclude is None:
            exclude = []
        else:
            exclude = list(self.exclude)
        exclude.extend(self.get_readonly_fields(request, obj))
        if self.exclude_unchecked:
            exclude.extend(self.exclude_unchecked)
        defaults = {
            "ct_field": self.ct_field,
            "fk_field": self.ct_fk_field,
            "form": self.form,
            "formfield_callback": curry(self.formfield_for_dbfield, request=request),
            "formset": self.formset,
            "extra": self.extra,
            "can_delete": self.can_delete,
            "can_order": False,
            "fields": fields,
            "max_num": self.max_num,
            "exclude": exclude
        }
        defaults.update(kwargs)   # Give the kwargs back
        return generic_inlineformset_factory(self.model, **defaults)

