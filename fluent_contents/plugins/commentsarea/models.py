from django.db import models
from django.utils.translation import ugettext_lazy as _
from fluent_contents.models import ContentItem


class CommentsAreaItem(ContentItem):
    allow_new = models.BooleanField(_("Allow posting new comments"), default=True)

    class Meta:
        verbose_name = _('Comments area')
        verbose_name_plural = _('Comments areas')

    def __unicode__(self):
        return u''
