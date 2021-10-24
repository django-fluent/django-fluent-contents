from django.db import models
from django.utils.translation import gettext_lazy as _

from fluent_contents.models import ContentItem, ContentItemManager


class DisqusCommentsAreaItem(ContentItem):
    allow_new = models.BooleanField(_("Allow posting new comments"), default=True)

    objects = ContentItemManager()  # Avoid Django 1.10 migrations

    class Meta:
        verbose_name = _("Disqus comments area")
        verbose_name_plural = _("Disqus comments areas")

    def __str__(self):
        return ""
