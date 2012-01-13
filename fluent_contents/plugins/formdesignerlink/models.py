from django.db import models
from django.utils.translation import ugettext_lazy as _
from fluent_contents.models import ContentItem
from form_designer.models import FormDefinition


class FormDesignerLink(ContentItem):
    form_definition = models.ForeignKey(FormDefinition, verbose_name=_('Form'))

    class Meta:
        verbose_name = _('Form link')
        verbose_name_plural = _('Form links')

    def __unicode__(self):
        return self.form_definition.title if self.form_definition else u''
