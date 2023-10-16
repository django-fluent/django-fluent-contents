from django.contrib import admin

from fluent_contents.admin import PlaceholderFieldAdmin

from .models import PlaceholderFieldTestPage


@admin.register(PlaceholderFieldTestPage)
class PlaceholderFieldTestPageAdmin(PlaceholderFieldAdmin):
    """
    Admin interface for the PlaceholderFieldTestPage model.
    """

    pass


