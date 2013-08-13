from django.contrib.contenttypes.generic import BaseGenericInlineFormSet
from django.contrib.contenttypes.models import ContentType


class BaseInitialGenericInlineFormSet(BaseGenericInlineFormSet):
    """
    A formset that can take initial values, and pass those to the generated forms.
    """
    # Based on http://stackoverflow.com/questions/442040/pre-populate-an-inline-formset/3766344#3766344

    def __init__(self, *args, **kwargs):
        """
        Grabs the curried initial values and stores them into a 'private' variable.
        """
        # This instance is created each time in the change_view() function.
        self._initial = kwargs.pop('initial', [])
        super(BaseInitialGenericInlineFormSet, self).__init__(*args, **kwargs)

    def initial_form_count(self):
        if self.is_bound:
            return super(BaseInitialGenericInlineFormSet, self).initial_form_count()
        else:
            return len(self.get_queryset())

    def total_form_count(self):
        if self.is_bound:
            return super(BaseInitialGenericInlineFormSet, self).total_form_count()
        else:
            return max(len(self.get_queryset()), len(self._initial)) + self.extra

    def _construct_form(self, i, **kwargs):
        if self._initial and not kwargs.get('instance', None):
            instance = None
            try:
                # Editing existing object. Make sure the ID is passed.
                instance = self.get_queryset()[i]
            except IndexError:
                try:
                    # Adding new object, pass initial values
                    # TODO: initial should be connected to proper instance ordering.
                    # currently this works, because the client handles all details for layout switching.
                    values = self._initial[i]
                    values[self.ct_field.name] = ContentType.objects.get_for_model(self.instance)
                    values[self.ct_fk_field.name] = self.instance.pk
                    instance = self.model(**values)
                except IndexError:
                    pass
            if instance:
                kwargs['instance'] = instance

        form = super(BaseInitialGenericInlineFormSet, self)._construct_form(i, **kwargs)
        return form
