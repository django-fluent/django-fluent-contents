from abc import abstractmethod
from django.contrib.admin.util import flatten_fieldsets
from django.contrib.contenttypes.generic import GenericInlineModelAdmin, generic_inlineformset_factory, BaseGenericInlineFormSet
from django.contrib.contenttypes.models import ContentType
from django.utils.functional import curry


class DynamicInlinesAdminMixin(object):
    """
    ModelAdmin mixin to create inlines with a :func:`get_inlines()` method.
    The initialization of the inlines is also delayed, reducing stress on the Django initialization sequence.
    """
    def __init__(self, *args, **kwargs):
        super(DynamicInlinesAdminMixin, self).__init__(*args, **kwargs)
        self._initialized_inlines = False

    def get_form(self, request, obj=None, **kwargs):
        """
        Lazy initialization of the inlines.
        """
        self._get_extra_inlines(obj)   # delayed the initialisation a bit
        return super(DynamicInlinesAdminMixin, self).get_form(request, obj, **kwargs)

    def _get_extra_inlines(self, obj=None):
        # When inlines are dynamically created, calling it too early places more stress on the Django load mechanisms.
        # This happens with plugin scanning code.
        #
        # e.g. load_middleware() -> import xyz.admin.something -> processes __init__.py ->
        #      admin.site.register(SomethingAdmin) -> Base::__init__() -> start looking for plugins -> ImportError
        #
        if not self._initialized_inlines:
            inlinetypes = self.get_extra_inlines(obj)
            for InlineType in inlinetypes:
                inline_instance = InlineType(self.model, self.admin_site)
                self.inline_instances.append(inline_instance)

            self._initialized_inlines = True

    @abstractmethod
    def get_extra_inlines(self, obj=None):
        """
        Overwrite this method to generate inlines.
        """
        raise NotImplementedError("The '{0}' subclass should implement get_extra_inlines()".format(self.__class__.__name__))



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

    def total_form_count(self):
        if self.is_bound:
            return super(BaseInitialGenericInlineFormSet, self).total_form_count()
        else:
            return len(self._initial) + self.extra

    def _construct_form(self, i, **kwargs):
        if self._initial and not kwargs.get('instance', None):
            try:
                # Editing existing object. Make sure the ID is passed.
                instance = self.get_queryset()[i]
            except IndexError:
                try:
                    # Adding new object, pass initial values
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

