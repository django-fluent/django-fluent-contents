from django.db import models

from fluent_contents.models import (
    ContentItem,
    ContentItemRelation,
    PlaceholderField,
    PlaceholderRelation,
)


class OverrideBase:
    # Needs to be in a different module for our tests.

    def get_render_template(self):
        pass


class TestPage(models.Model):
    """
    A plain model, for testing placeholders.
    """

    contents = models.TextField("Contents")

    def __str__(self):
        return self.contents

    class Meta:
        app_label = "testapp"
        verbose_name = "Test page"
        verbose_name_plural = "Test pages"


class PlaceholderFieldTestPage(models.Model):
    """
    A model with PlaceholderField, for testing,
    """

    title = models.CharField(max_length=200)
    contents = PlaceholderField("field_slot1")

    placeholder_set = PlaceholderRelation()
    contentitem_set = ContentItemRelation()

    class Meta:
        app_label = "testapp"
        verbose_name = "Test page"
        verbose_name_plural = "Test pages"

    def __str__(self):
        return self.title


class RawHtmlTestItem(ContentItem):
    """
    The most basic "raw HTML" content item, for testing.
    """

    html = models.TextField("HTML code")

    class Meta:
        app_label = "testapp"
        verbose_name = "Test HTML code"
        verbose_name_plural = "Test HTML codes"

    def __str__(self):
        return self.html


class TimeoutTestItem(ContentItem):
    """
    The most basic "raw HTML" content item, for testing.
    """

    html = models.TextField("HTML code")

    class Meta:
        app_label = "testapp"
        verbose_name = "Timeout test"
        verbose_name_plural = "Timeout test"

    def __str__(self):
        return self.html


class MediaTestItem(ContentItem):
    """
    The most basic "media HTML" content item, for testing.
    """

    html = models.TextField("HTML code")

    class Meta:
        app_label = "testapp"
        verbose_name = "Media test"
        verbose_name_plural = "Media test"

    def __str__(self):
        return self.html


class RedirectTestItem(ContentItem):
    """
    The most basic "media HTML" content item, for testing.
    """

    html = models.TextField("HTML code")

    class Meta:
        app_label = "testapp"
        verbose_name = "Redirect test"
        verbose_name_plural = "Redirect test"

    def __str__(self):
        return self.html
