from future.utils import python_2_unicode_compatible
from django.db import models
from django.utils.translation import ugettext_lazy as _
from fluent_contents.models import ContentItem, ContentItemManager
from form_designer.models import FormDefinition


@python_2_unicode_compatible
class FormDesignerLink(ContentItem):
    form_definition = models.ForeignKey(FormDefinition, verbose_name=_('Form'))

    objects = ContentItemManager()  # Avoid Django 1.10 migrations

    class Meta:
        verbose_name = _('Form link')
        verbose_name_plural = _('Form links')

    def __str__(self):
        return self.form_definition.title if self.form_definition else u''
