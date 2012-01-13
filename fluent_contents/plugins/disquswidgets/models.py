from django.db import models
from django.utils.translation import ugettext_lazy as _
from fluent_contents.models import ContentItem


class DisqusCommentsAreaItem(ContentItem):
    allow_new = models.BooleanField(_("Allow posting new comments"), default=True)

    class Meta:
        verbose_name = _('Disqus comments area')
        verbose_name_plural = _('Disqus comments areas')

    def __unicode__(self):
        return u''