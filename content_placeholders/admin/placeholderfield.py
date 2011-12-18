from django.contrib import admin
from content_placeholders import extensions
from content_placeholders.admin.placeholdereditor import PlaceholderEditorInline, PlaceholderEditorAdminMixin
from content_placeholders.models import PlaceholderData
from content_placeholders.models.fields import PlaceholderField


class PlaceholderFieldInline(PlaceholderEditorInline):
    template = "admin/content_placeholders/placeholderfield/inline_init.html"


class PlaceholderFieldAdminMixin(PlaceholderEditorAdminMixin):
    """
    The base functionality for ``ModelAdmin`` dialogs to display placeholder fields.
    """
    placeholder_inline = PlaceholderFieldInline


    def get_placeholder_data(self, request, obj):
        # Return all placeholder fields in the model.
        if not hasattr(self.model._meta, 'placeholder_fields'):
            return []

        data = []
        for name, field in self.model._meta.placeholder_fields.iteritems():
            assert isinstance(field, PlaceholderField)
            data.append(PlaceholderData(
                slot=field.slot,
                title=field.verbose_name.capitalize(),
            ))

        return data


    def get_all_allowed_plugins(self):
        # Get all allowed plugins of the various placeholders together.
        if not hasattr(self.model._meta, 'placeholder_fields'):
            # No placeholder fields in the model, no need for inlines.
            return []

        plugins = []
        for name, field in self.model._meta.placeholder_fields.iteritems():
            assert isinstance(field, PlaceholderField)
            if field.plugins is None:
                # no limitations, so all is allowed
                return extensions.plugin_pool.get_plugins()
            else:
                plugins += field.plugins

        return list(set(plugins))


class PlaceholderFieldAdmin(PlaceholderFieldAdminMixin, admin.ModelAdmin):
    """
    Base class for ``ModelAdmin`` instances that display :class:`~content_placeholders.models.fields.PlaceholderField` values.
    The class is built up with a :class:`PlaceholderFieldAdminMixin` mixin, allowing inheritance from the ``MPTTModelAdmin`` class instead.
    """
    pass
