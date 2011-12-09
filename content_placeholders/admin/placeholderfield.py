from django.contrib import admin
from content_placeholders.admin.placeholdereditor import PlaceholderEditorAdminMixin
from content_placeholders.models import PlaceholderData
from content_placeholders.models.fields import PlaceholderField



class PlaceholderFieldAdminMixin(PlaceholderEditorAdminMixin):
    """
    The base functionality for ``ModelAdmin`` dialogs to display placeholder fields.
    """
    # Currently reusing the placeholder editor.

    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Render the ``PlaceholderField`` with the proper form widget.
        Avoid getting the '+' sign to add a new field.
        """
        if isinstance(db_field, PlaceholderField):
            return db_field.formfield_for_admin(**kwargs)
        return super(PlaceholderFieldAdminMixin, self).formfield_for_dbfield(db_field, **kwargs)


    def get_placeholder_data(self, request, obj):
        # Return all placeholder fields in the model.
        data = []
        for field in self.model._meta.fields:
            if isinstance(field, PlaceholderField):
                data.append(PlaceholderData(
                    slot=field.slotname
                ))

        return data



class PlaceholderFieldAdmin(PlaceholderFieldAdminMixin, admin.ModelAdmin):
    """
    Base class for ``ModelAdmin`` instances that display :class:`~content_placeholders.models.fields.PlaceholderField` values.
    The class is built up with a :class:`PlaceholderFieldAdminMixin` mixin, allowing inheritance from the ``MPTTModelAdmin`` class instead.
    """
    pass
