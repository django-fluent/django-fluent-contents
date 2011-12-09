from abc import abstractmethod
from django.contrib import admin
from django.utils.functional import curry
from content_placeholders import extensions
from content_placeholders.admin.contentitems import get_content_item_inlines
from content_placeholders.admin.genericextensions import ExtensibleGenericInline, BaseInitialGenericInlineFormSet, DynamicInlinesAdminMixin
from content_placeholders.analyzer import get_placeholder_data
from content_placeholders.models import Placeholder, PlaceholderData
from content_placeholders.models.fields import PlaceholderField


class PlaceholderInline(ExtensibleGenericInline):
    model = Placeholder
    formset = BaseInitialGenericInlineFormSet
    ct_field = 'parent_type'
    ct_fk_field = 'parent_id'
    template = "admin/content_placeholders/placeholder/inline_tabs.html"
    extra = 0

    class Media:
        # cp_tabs.js is included here, as it's a presentation choice
        # to display the placeholder panes in a tabbar format.
        # The remaining scripts should just operate the same without it.
        js = (
            'content_placeholders/admin/cp_admin.js',
            'content_placeholders/admin/cp_data.js',
            'content_placeholders/admin/cp_tabs.js',
            'content_placeholders/admin/cp_plugins.js',
        )
        css = {
            'screen': (
                'content_placeholders/admin/cp_admin.css',
            ),
        }

        extend = False   # No need for the standard 'admin/js/inlines.min.js' here.

    def get_all_allowed_plugins(self):
        """
        Return all plugin categories which can be used by placeholder content.
        """
        return extensions.plugin_pool.get_plugins()


    def get_formset(self, request, obj=None, **kwargs):
        """
        Pre-populating formset using GET params
        """
        # Note this method is called twice, the second time in get_fieldsets() as `get_formset(request).form`
        initial = []
        if request.method == "GET":
            placeholder_admin = self.admin_site._registry[self.parent_model]   # HACK: accessing private field.

            # Grab the initial data from the parent PlaceholderFieldAdminMixin
            data = placeholder_admin.get_placeholder_data(request, obj)
            initial = self._get_initial_from_placeholderdata(data)

        # Inject as default parameter to the constructor
        # This is the BaseExtendedGenericInlineFormSet constructor
        formset = super(PlaceholderInline, self).get_formset(request, obj, **kwargs)
        formset.__init__ = curry(formset.__init__, initial=initial)
        return formset


    def _get_initial_from_placeholderdata(self, data):
        # data = list(PlaceholderData)
        return [{
                'slot': d.slot,
                'title': d.title
            }
            for d in data
        ]



class PlaceholderFieldAdminMixin(object):  # admin.ModelAdmin
    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Render the ``PlaceholderField`` with the proper form widget.
        Avoid getting the '+' sign to add a new field.
        """
        if isinstance(db_field, PlaceholderField):
            return db_field.formfield_for_admin(**kwargs)
        return super(PlaceholderFieldAdminMixin, self).formfield_for_dbfield(db_field, **kwargs)


    @abstractmethod
    def get_object_template(self, request, obj):
        """
        Return the template for an object, from which the placeholders are extracted.
        Either this method needs to be overwritten, or :func:`get_placeholder_data` should be overwritten.
        """
        raise NotImplementedError("The '{0}' subclass should implement get_object_template() or get_placeholder_data().".format(self.__class__.__name__))


    def get_placeholder_data(self, request, obj):
        """
        Return a list of :class:`content_placeholders.analyzer.PlaceholderData`` objects, that will be displayed as tabs in the editor.
        This method calls :func:`get_object_template` by default, extracting placeholder data
        with :func:`~content_placeholders.analyzer.get_placeholder_data`.
        """
        template = self.get_object_template(request, obj)
        return get_placeholder_data(template)


class PlaceholderFieldAdmin(PlaceholderFieldAdminMixin, DynamicInlinesAdminMixin, admin.ModelAdmin):
    """
    Base class for ``ModelAdmin`` instances that display :class:`~content_placeholders.models.fields.PlaceholderField` values.
    """

    def get_extra_inlines(self, obj=None):
        # Currently reusing the placeholder editor.
        return [PlaceholderInline] + get_content_item_inlines()


    def get_placeholder_data(self, request, obj):
        # Return all placeholder fields in the model.
        data = []
        for field in self.model._meta.fields:
            if isinstance(field, PlaceholderField):
                data.append(PlaceholderData(
                    slot=field.slotname
                ))

        return data
