from abc import abstractmethod
from django.contrib.admin import ModelAdmin
from django.contrib.admin.util import flatten_fieldsets
from django.contrib.contenttypes.generic import GenericInlineModelAdmin, generic_inlineformset_factory, BaseGenericInlineFormSet
from django.contrib.contenttypes.models import ContentType
from django.utils.functional import curry


class DynamicInlinesModelAdmin(ModelAdmin):
    """
    ModelAdmin mixin to create inlines with a :func:`get_inlines()` method.
    The initialization of the inlines is also delayed, reducing stress on the Django initialization sequence.
    """
    extra_inlines_first = True

    @abstractmethod
    def get_extra_inlines(self):
        """
        Overwrite this method to generate inlines.
        """
        raise NotImplementedError("The '{0}' subclass should implement get_extra_inlines()".format(self.__class__.__name__))


    # Django 1.3:
    # Inlines are created once in self.inline_instances

    def __init__(self, *args, **kwargs):
        super(DynamicInlinesModelAdmin, self).__init__(*args, **kwargs)
        self._initialized_inlines = False

    def get_form(self, request, obj=None, **kwargs):
        if hasattr(self, 'inline_instances') \
        and not self._initialized_inlines:
            # delayed the initialisation a bit
            # When inlines are dynamically created, calling it too early places more stress on the Django load mechanisms.
            # This happens with plugin scanning code.
            #
            # e.g. load_middleware() -> import xyz.admin.something -> processes __init__.py ->
            #      admin.site.register(SomethingAdmin) -> Base::__init__() -> start looking for plugins -> ImportError
            #
            if self.extra_inlines_first:
                self.inline_instances = self._get_extra_inline_instances() + self.inline_instances
            else:
                self.inline_instances += self._get_extra_inline_instances()
            self._initialized_inlines = True
        return super(DynamicInlinesModelAdmin, self).get_form(request, obj, **kwargs)


    def _get_extra_inline_instances(self):
        inline_instances = []
        inlinetypes = self.get_extra_inlines()
        for InlineType in inlinetypes:
            inline_instance = InlineType(self.model, self.admin_site)
            inline_instances.append(inline_instance)
        return inline_instances


    # Django 1.4:
    # Inlines are created per request

    def get_inline_instances(self, request):
        inlines = super(DynamicInlinesModelAdmin, self).get_inline_instances(request)
        if self.extra_inlines_first:
            return self._get_extra_inline_instances() + inlines
        else:
            return inlines + self._get_extra_inline_instances()



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


class ExtensibleGenericInline(GenericInlineModelAdmin):
    """
    Custom :class:`~django.contrib.contenttypes.generic.GenericInlineModelAdmin` subclass
    that got some of it's extensibility back.
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

