from django.contrib import admin
from fluent_contents.admin import PlaceholderFieldAdmin
from .models import PlaceholderFieldTestPage


class PlaceholderFieldTestPageAdmin(PlaceholderFieldAdmin):
    """
    Admin interface for the PlaceholderFieldTestPage model.
    """
    pass


admin.site.register(PlaceholderFieldTestPage, PlaceholderFieldTestPageAdmin)
