from future.utils import python_2_unicode_compatible
from django.db import models
from fluent_contents.models import ContentItem, ContainerItem, PlaceholderField, PlaceholderRelation, ContentItemRelation, get_parent_language_code


class OverrideBase(object):
    # Needs to be in a different module for our tests.

    def get_render_template(self):
        pass


@python_2_unicode_compatible
class TestPage(models.Model):
    """
    A plain model, for testing placeholders.
    """
    contents = models.TextField("Contents")

    def __str__(self):
        return self.contents

    class Meta:
        app_label = 'testapp'
        verbose_name = "Test page"
        verbose_name_plural = "Test pages"


@python_2_unicode_compatible
class PlaceholderFieldTestPage(models.Model):
    """
    A model with PlaceholderField, for testing,
    """
    title = models.CharField(max_length=200)
    contents = PlaceholderField("field_slot1")

    # The language code is editable for testing.
    # This attribute is read by
    language_code = models.CharField(max_length=10, default='en')

    placeholder_set = PlaceholderRelation()
    contentitem_set = ContentItemRelation()

    class Meta:
        app_label = 'testapp'
        verbose_name = "Test page"
        verbose_name_plural = "Test pages"

    def __str__(self):
        return self.title

assert get_parent_language_code(PlaceholderFieldTestPage(language_code='nl')) == 'nl'


@python_2_unicode_compatible
class RawHtmlTestItem(ContentItem):
    """
    The most basic "raw HTML" content item, for testing.
    """
    html = models.TextField("HTML code")

    class Meta:
        app_label = 'testapp'
        verbose_name = 'Test HTML code'
        verbose_name_plural = 'Test HTML codes'

    def __str__(self):
        return self.html


@python_2_unicode_compatible
class TimeoutTestItem(ContentItem):
    """
    The most basic "raw HTML" content item, for testing.
    """
    html = models.TextField("HTML code")

    class Meta:
        app_label = 'testapp'
        verbose_name = 'Timeout test'
        verbose_name_plural = 'Timeout test'

    def __str__(self):
        return self.html


@python_2_unicode_compatible
class MediaTestItem(ContentItem):
    """
    The most basic "media HTML" content item, for testing.
    """
    html = models.TextField("HTML code")

    class Meta:
        app_label = 'testapp'
        verbose_name = 'Media test'
        verbose_name_plural = 'Media test'

    def __str__(self):
        return self.html


@python_2_unicode_compatible
class RedirectTestItem(ContentItem):
    """
    The most basic "media HTML" content item, for testing.
    """
    html = models.TextField("HTML code")

    class Meta:
        app_label = 'testapp'
        verbose_name = 'Redirect test'
        verbose_name_plural = 'Redirect test'

    def __str__(self):
        return self.html


@python_2_unicode_compatible
class ContainerTestItem(ContainerItem):
    """
    The most basic "raw HTML" content item, for testing.
    """
    tag = models.CharField(max_length=20)
    css_class = models.CharField(max_length=200)

    class Meta:
        app_label = 'testapp'
        verbose_name = 'Container test'
        verbose_name_plural = 'Container test'

    def __str__(self):
        return self.tag
