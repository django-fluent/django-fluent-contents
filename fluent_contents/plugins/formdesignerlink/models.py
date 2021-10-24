from django.db import models
from django.utils.translation import gettext_lazy as _
from form_designer.models import FormDefinition

from fluent_contents.models import ContentItem, ContentItemManager


class FormDesignerLink(ContentItem):
    form_definition = models.ForeignKey(
        FormDefinition, on_delete=models.PROTECT, verbose_name=_("Form")
    )

    objects = ContentItemManager()  # Avoid Django 1.10 migrations

    class Meta:
        verbose_name = _("Form link")
        verbose_name_plural = _("Form links")

    def __str__(self):
        return self.form_definition.title if self.form_definition else ""
