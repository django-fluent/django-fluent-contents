from abc import abstractmethod
from django.contrib import admin
from django.utils.functional import curry
from content_placeholders import extensions
from content_placeholders.admin.contentitems import get_content_item_inlines
from content_placeholders.admin.genericextensions import ExtensibleGenericInline, BaseInitialGenericInlineFormSet, DynamicInlinesAdminMixin
from content_placeholders.models import Placeholder


class PlaceholderEditorInline(ExtensibleGenericInline):
    """
    The placeholder editor, implemented as an admin inline.
    It displays tabs for each inline placeholder, and displays ``ContentItem`` plugins in the tabs.

    It should be inserted in the ``ModelAdmin.inlines`` before the inlines that
    the :func:`~content_placeholders.admin.contentitems.get_content_item_inlines` function generates.
    The ContentItem inlines look for the ``Placeholder`` object that was created just before their invocation.
    """
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
        It accesses the parent :class:`PlaceholderEditorBaseMixin` by default to request the information.
        This field is used in the template.
        """
        return self._get_parent_modeladmin().get_all_allowed_plugins()


    def get_formset(self, request, obj=None, **kwargs):
        """
        Pre-populate formset with the initial placeholders to display.
        """
        # Note this method is called twice, the second time in get_fieldsets() as `get_formset(request).form`
        initial = []
        if request.method == "GET":
            placeholder_admin = self._get_parent_modeladmin()

            # Grab the initial data from the parent PlaceholderEditorBaseMixin
            data = placeholder_admin.get_placeholder_data(request, obj)
            initial = self._get_initial_from_placeholderdata(data)

        # Inject as default parameter to the constructor
        # This is the BaseExtendedGenericInlineFormSet constructor
        formset = super(PlaceholderEditorInline, self).get_formset(request, obj, **kwargs)
        formset.__init__ = curry(formset.__init__, initial=initial)
        return formset


    def _get_initial_from_placeholderdata(self, data):
        # data = list(PlaceholderData)
        return [d.as_dict()
            for d in data
        ]


    def _get_parent_modeladmin(self):
        # HACK: accessing private field.
        parentadmin = self.admin_site._registry[self.parent_model]

        # Do some "type" checking to developers are aided in inheriting their parent ModelAdmin screens with the proper classes.
        assert isinstance(parentadmin, PlaceholderEditorBaseMixin), "The '{0}' class can only be used in admin screens which implement a PlaceholderEditor mixin class.".format(self.__class__.__name__)
        return parentadmin



class PlaceholderEditorBaseMixin(object):
    """
    Base mixin for a ``ModelAdmin`` to provide the :class:`PlaceholderEditorInline` with initial data.
    """
    @abstractmethod
    def get_placeholder_data(self, request, obj):
        """
        Return the placeholders that the editor should initially display.
        The function should return a list of :class:`~content_placeholders.models.PlaceholderData` classes.
        These classes can either be instantiated manually, or read from a template
        using :func:`~content_placeholders.analyzer.get_template_placeholder_data` for example.
        """
        raise NotImplementedError("The '{0}' subclass should implement get_placeholder_data().".format(self.__class__.__name__))


    def get_all_allowed_plugins(self):
        """
        Return all plugin categories which can be used by placeholder content.
        By default, all plugins are allowed.
        """
        return extensions.plugin_pool.get_plugins()



class PlaceholderEditorAdminMixin(PlaceholderEditorBaseMixin, DynamicInlinesAdminMixin):  # admin.ModelAdmin
    """
    The base functionality for ``ModelAdmin`` dialogs to display a placeholder editor with plugins.
    """
    def get_extra_inlines(self, obj=None):
        return [PlaceholderEditorInline] + get_content_item_inlines(plugins=self.get_all_allowed_plugins())



class PlaceholderEditorAdmin(PlaceholderEditorAdminMixin, admin.ModelAdmin):
    """
    Base class for ``ModelAdmin`` instaces to display the placeholder editor.
    The class is built up with a :class:`PlaceholderEditorAdminMixin` mixin, allowing inheritance from the ``MPTTModelAdmin`` class instead.
    """
    pass
