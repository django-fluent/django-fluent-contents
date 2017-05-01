from django.contrib.contenttypes.forms import BaseGenericInlineFormSet
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.forms.formsets import ManagementForm



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

    @property
    def management_form(self):
        try:
            return super(BaseInitialGenericInlineFormSet, self).management_form
        except ValidationError:
            # Provide with better description of what is happening.
            form = ManagementForm(self.data, auto_id=self.auto_id, prefix=self.prefix)
            if not form.is_valid():
                raise ValidationError(
                    u'ManagementForm data is missing or has been tampered with.'
                    u' form: {0}, model: {1}, errors: \n{2}'.format(
                        self.__class__.__name__, self.model.__name__,
                        form.errors.as_text()
                ))
            else:
                raise

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
            instance = self.__get_form_instance(i)
            if instance:
                kwargs['instance'] = instance

        form = super(BaseInitialGenericInlineFormSet, self)._construct_form(i, **kwargs)
        return form

    def __initial_minus_queryset(self):
        """
        Gives all elements from self._initial having a slot value that is not already
        in self.get_queryset()
        """
        queryset = self.get_queryset()

        def initial_not_in_queryset(initial):
            for x in queryset:
                if x.slot == initial['slot']:
                    return False

            return True

        return list(filter(initial_not_in_queryset, self._initial))

    def __get_form_instance(self, i):
        instance = None
        try:
            # Editing existing object. Make sure the ID is passed.
            instance = self.get_queryset()[i]
        except IndexError:
            try:
                # Adding new object, pass initial values
                # TODO: initial should be connected to proper instance ordering.
                # currently this works, because the client handles all details for layout switching.
                queryset_count = self.get_queryset().count()
                values = self.__initial_minus_queryset()[i - queryset_count]

                values[self.ct_field.name] = ContentType.objects.get_for_model(self.instance)
                values[self.ct_fk_field.name] = self.instance.pk
                instance = self.model(**values)
            except IndexError:
                pass

        return instance
