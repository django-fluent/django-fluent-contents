from future.utils import python_2_unicode_compatible
from django.db import models
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _
from fluent_contents.models import ContentItem, ContentItemManager


@python_2_unicode_compatible
class RawHtmlItem(ContentItem):
    html = models.TextField(_('HTML code'), help_text=_("Enter the HTML code to display, like the embed code of an online widget."))

    objects = ContentItemManager()  # Avoid Django 1.10 migrations

    class Meta:
        verbose_name = _('HTML code')
        verbose_name_plural = _('HTML code')

    def __str__(self):
        return strip_tags(self.html).strip()
