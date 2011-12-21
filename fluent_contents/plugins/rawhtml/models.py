from django.db import models
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _
from fluent_contents.models import ContentItem

class RawHtmlItem(ContentItem):
    html = models.TextField(_('HTML code'), help_text=_("Enter the HTML code to display, like the embed code of an online widget."))

    class Meta:
        verbose_name = _('HTML code')
        verbose_name_plural = _('HTML code')

    def __unicode__(self):
        return strip_tags(self.html)
