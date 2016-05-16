from abc import abstractmethod
import django
from django.conf import settings
from django.conf.urls import url
from django.contrib.admin import ModelAdmin
from django.contrib.admin.helpers import InlineAdminFormSet
from django.core.exceptions import ImproperlyConfigured
from django.db.models import signals
from django.dispatch import receiver
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.functional import curry
from fluent_contents import extensions
from fluent_contents.admin.contentitems import get_content_item_inlines, BaseContentItemFormSet
from fluent_contents.admin.genericextensions import BaseInitialGenericInlineFormSet
from fluent_contents.models import Placeholder
from fluent_contents.models.managers import get_parent_active_language_choices
from fluent_utils.ajax import JsonResponse

try:
    from django.contrib.contenttypes.admin import GenericInlineModelAdmin  # Django 1.7
except ImportError:
    from django.contrib.contenttypes.generic import GenericInlineModelAdmin


class PlaceholderInlineFormSet(BaseInitialGenericInlineFormSet):
    # Most logic happens in the generic base class

    def __init__(self, *args, **kwargs):
        self._instance_languages = None
        #kwargs['prefix'] = 'placeholder_fs'
        super(PlaceholderInlineFormSet, self).__init__(*args, **kwargs)

    @classmethod
    def get_default_prefix(cls):
        # Make output less verbose, easier to read, and less kB to transmit.
        return 'placeholder-fs'

    @property
    def other_instance_languages(self):
        return get_parent_active_language_choices(self.instance, exclude_current=True)


class PlaceholderEditorInline(GenericInlineModelAdmin):
    """
    The placeholder editor, implemented as an admin inline.
    It displays tabs for each inline placeholder, and displays :class:`~fluent_contents.models.ContentItem` plugins in the tabs.

    It should be inserted in the ``ModelAdmin.inlines`` before the inlines that
    the :func:`~fluent_contents.admin.get_content_item_inlines` function generates.
    The ContentItem inlines look for the ``Placeholder`` object that was created just before their invocation.

    To fetch the initial data, the inline will attempt to find the parent model,
    and call :func:`~PlaceholderEditorBaseMixin.get_placeholder_data`.
    When the admin models inherit from :class:`~fluent_contents.admin.PlaceholderEditorAdmin`
    or :class:`~fluent_contents.admin.PlaceholderFieldAdmin` this will be setup already.
    """
    model = Placeholder
    formset = PlaceholderInlineFormSet  # Important part of the class!
    ct_field = 'parent_type'
    ct_fk_field = 'parent_id'
    template = "admin/fluent_contents/placeholder/inline_tabs.html"
    extra = 0
    is_fluent_editor_inline = True  # Allow admin templates to filter the inlines

    class Media:
        # cp_tabs.js is included here, as it's a presentation choice
        # to display the placeholder panes in a tabbar format.
        # The remaining scripts should just operate the same without it.
        js = (
            'fluent_contents/admin/jquery.cookie.js',
            'fluent_contents/admin/cp_admin.js',
            'fluent_contents/admin/cp_data.js',
            'fluent_contents/admin/cp_tabs.js',
            'fluent_contents/admin/cp_plugins.js',
            'fluent_contents/admin/cp_widgets.js',
            'fluent_contents/admin/fluent_contents.js',
        )
        #if 'grapelli' in settings.INSTALLED_APPS:
        # ...
        if 'flat' in settings.INSTALLED_APPS or django.VERSION >= (1, 9):
            css = {
                'screen': (
                    'fluent_contents/admin/cp_admin.css',
                    'fluent_contents/admin/cp_admin_flat.css',
                ),
            }
        else:
            css = {
                'screen': (
                    'fluent_contents/admin/cp_admin.css',
                    'fluent_contents/admin/cp_admin_classic.css',
                ),
            }

        extend = False   # No need for the standard 'admin/js/inlines.min.js' here.

    def get_all_allowed_plugins(self):
        """
        Return *all* plugin categories which can be used by placeholder content.
        This is the sum of all allowed plugins by the various slots on the page.
        It accesses the parent :class:`PlaceholderEditorBaseMixin` by default to request the information.
        This field is used in the template.
        """
        return self._get_parent_modeladmin().get_all_allowed_plugins()

    def get_formset(self, request, obj=None, **kwargs):
        """
        Pre-populate formset with the initial placeholders to display.
        """
        def _placeholder_initial(p):
            # p.as_dict() returns allowed_plugins too for the client-side API.
            return {
                'slot': p.slot,
                'title': p.title,
                'role': p.role,
            }

        # Note this method is called twice, the second time in get_fieldsets() as `get_formset(request).form`
        initial = []
        if request.method == "GET":
            placeholder_admin = self._get_parent_modeladmin()

            # Grab the initial data from the parent PlaceholderEditorBaseMixin
            data = placeholder_admin.get_placeholder_data(request, obj)
            initial = [_placeholder_initial(d) for d in data]

            # Order initial properly,

        # Inject as default parameter to the constructor
        # This is the BaseExtendedGenericInlineFormSet constructor
        FormSetClass = super(PlaceholderEditorInline, self).get_formset(request, obj, **kwargs)
        FormSetClass.__init__ = curry(FormSetClass.__init__, initial=initial)
        return FormSetClass

    def _get_parent_modeladmin(self):
        # HACK: accessing private field.
        try:
            parentadmin = self.admin_site._registry[self.parent_model]
        except KeyError:
            raise ImproperlyConfigured("Model admin for '{0}' not found in admin_site!".format(self.parent_model.__name__))

        # Do some "type" checking to developers are aided in inheriting their parent ModelAdmin screens with the proper classes.
        assert isinstance(parentadmin, PlaceholderEditorBaseMixin), "The '{0}' class can only be used in admin screens which implement a PlaceholderEditor mixin class.".format(self.__class__.__name__)
        return parentadmin


class PlaceholderEditorBaseMixin(object):
    """
    Base interface/mixin for a :class:`~django.contrib.admin.ModelAdmin` to provide the :class:`PlaceholderEditorInline` with initial data.
    This class is implemented by the :class:`PlaceholderEditorAdmin` and :class:`~fluent_contents.admin.PlaceholderFieldAdmin` classes.
    """
    @abstractmethod
    def get_placeholder_data(self, request, obj=None):
        """
        Return the placeholders that the editor should initially display.
        The function should return a list of :class:`~fluent_contents.models.PlaceholderData` classes.
        These classes can either be instantiated manually, or read from a template
        using the :ref:`fluent_contents.analyzer` module for example.
        """
        # This information will be read by the PlaceholderEditorInline,
        # but it could also be reused by other derived classes off course.
        raise NotImplementedError("The '{0}' subclass should implement get_placeholder_data().".format(self.__class__.__name__))

    def get_all_allowed_plugins(self):
        """
        Return all plugin categories which can be used by placeholder content.
        By default, all plugins are allowed. Individual slot names may further limit the plugin set.

        :rtype: list of :class:`~fluent_contents.extensions.ContentPlugin`
        """
        return extensions.plugin_pool.get_plugins()


class PlaceholderEditorAdmin(PlaceholderEditorBaseMixin, ModelAdmin):
    """
    The base functionality for :class:`~django.contrib.admin.ModelAdmin` dialogs to display a placeholder editor with plugins.
    It loads the inlines using :func:`get_extra_inlines`.

    It loads the :class:`PlaceholderEditorInline`, which displays each placeholder in separate tabs:

    .. image:: /images/admin/placeholdereditoradmin2.png
       :width: 755px
       :height: 418px
       :alt: django-fluent-contents placeholder editor preview
    """
    placeholder_inline = PlaceholderEditorInline

    def get_inline_instances(self, request, *args, **kwargs):
        """
        Create the inlines for the admin, including the placeholder and contentitem inlines.
        """
        # Django 1.3: inlines were created once in self.inline_instances (not supported anymore)
        # Django 1.4: inlines are created per request
        # Django 1.5: 'obj' parameter was added so it can be passed to 'has_change_permission' and friends.
        inlines = super(PlaceholderEditorAdmin, self).get_inline_instances(request, *args, **kwargs)

        extra_inline_instances = []
        inlinetypes = self.get_extra_inlines()
        for InlineType in inlinetypes:
            inline_instance = InlineType(self.model, self.admin_site)
            extra_inline_instances.append(inline_instance)

        return extra_inline_instances + inlines

    def get_extra_inlines(self):
        """
        Return the extra inlines for the placeholder editor.
        It loads the :attr:`placeholder_inline` first, followed by the inlines for the :class:`~fluent_contents.models.ContentItem` classes.
        """
        return [self.placeholder_inline] + get_content_item_inlines(plugins=self.get_all_allowed_plugins())

    def get_urls(self):
        urls = super(PlaceholderEditorAdmin, self).get_urls()
        info = _get_url_format(self.model._meta)
        return [
            url(
                r'^(?P<object_id>\d+)/api/get_placeholder_data/',
                self.admin_site.admin_view(self.get_placeholder_data_view),
                name='{0}_{1}_get_placeholder_data'.format(*info)
            )
        ] + urls

    def get_placeholder_data_view(self, request, object_id):
        """
        Return the placeholder data as dictionary.
        This is used in the client for the "copy" functionality.
        """
        language = 'en'  #request.POST['language']
        with translation.override(language):  # Use generic solution here, don't assume django-parler is used now.
            obj = self.get_object(request, object_id)

        if obj is None:
            json = {'success': False, 'error': 'Page not found'}
            status = 404
        elif not self.has_change_permission(request, obj):
            json = {'success': False, 'error': 'No access to page'}
            status = 403
        else:
            # Fetch the forms that would be displayed,
            # return the data as serialized form data.
            status = 200
            json = {
                'success': True,
                'object_id': object_id,
                'language_code': language,
                'formset_forms': self._get_object_formset_data(request, obj),
            }

        return JsonResponse(json, status=status)

    def _get_object_formset_data(self, request, obj):
        inline_instances = self.get_inline_instances(request, obj)
        placeholder_slots = dict(Placeholder.objects.parent(obj).values_list('id', 'slot'))
        all_forms = []

        for FormSet, inline in zip(self.get_formsets(request, obj), inline_instances):
            # Only ContentItem inlines
            if isinstance(inline, PlaceholderEditorInline) \
            or not getattr(inline, 'is_fluent_editor_inline', False):
                continue

            formset_forms = self._get_contentitem_formset_html(request, obj, FormSet, inline, placeholder_slots)
            if formset_forms:
                all_forms.extend(formset_forms)

        # Flatten list, sorted on insertion for the client.
        all_forms.sort(key=lambda x: (x['placeholder_slot'], x['sort_order']))
        return all_forms

    def _get_contentitem_formset_html(self, request, obj, FormSet, inline, placeholder_slots):
        # Passing serialized object fields to the client doesn't work,
        # as some form fields (e.g. picture field or MultiValueField) have a different representation.
        # The only way to pass a form copy to the client is by actually rendering it.
        # Hence, emulating change_view code here:
        if django.VERSION >= (1, 6):
            queryset = inline.get_queryset(request)
        else:
            queryset = inline.queryset(request)

        formset = FormSet(instance=obj, prefix='', queryset=queryset)
        fieldsets = list(inline.get_fieldsets(request, obj))
        readonly = list(inline.get_readonly_fields(request, obj))
        prepopulated = dict(inline.get_prepopulated_fields(request, obj))
        inline.extra = 0
        inline_admin_formset = InlineAdminFormSet(inline, formset, fieldsets, prepopulated, readonly, model_admin=self)

        form_data = []
        for i, inline_admin_form in enumerate(inline_admin_formset):
            if inline_admin_form.original is None:  # The extra forms
                continue

            # exactly what admin/fluent_contents/contentitem/inline_container.html does:
            template_name = inline_admin_formset.opts.cp_admin_form_template
            form_html = render_to_string(template_name, {
                'inline_admin_form': inline_admin_form,
                'inline_admin_formset': inline_admin_formset,
                'original': obj,
                'object_id': obj.pk,
                'add': False,
                'change': True,
                'has_change_permission': True,
            }, context_instance=RequestContext(request))

            # Append to list with metadata included
            contentitem = inline_admin_form.original
            form_data.append({
                'contentitem_id': contentitem.pk,
                'sort_order': contentitem.sort_order,
                'placeholder_id': contentitem.placeholder_id,
                'placeholder_slot': placeholder_slots[contentitem.placeholder_id],
                'html': form_html,
                'plugin': inline.plugin.__class__.__name__,
                'model': inline.model.__name__,
                'prefix': formset.add_prefix(i),
            })
        return form_data

    def save_formset(self, request, form, formset, change):
        # Track deletion of Placeholders across the formsets.
        # When a Placeholder is deleted, the ContentItem can't be saved anymore with the old placeholder_id
        # That ID did exist at the beginning of the transaction, but won't be when all forms are saved.
        # Pass the knowledge of deleted placeholders to the ContentItem formset, so it can deal with it.
        if isinstance(formset, BaseContentItemFormSet):
            formset._deleted_placeholders = getattr(request, '_deleted_placeholders', ())

        saved_instances = super(PlaceholderEditorAdmin, self).save_formset(request, form, formset, change)

        if isinstance(formset, PlaceholderInlineFormSet):
            request._deleted_placeholders = [obj._old_pk for obj in formset.deleted_objects]

        return saved_instances


@receiver(signals.post_delete, sender=Placeholder)
def _get_pk_on_placeholder_delete(instance, **kwargs):
    # Make sure the old PK can still be tracked
    instance._old_pk = instance.pk


def _get_url_format(opts):
    try:
        return opts.app_label, opts.model_name  # Django 1.7 format
    except AttributeError:
        return opts.app_label, opts.module_name
