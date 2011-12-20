from django.db import models
from django.utils.translation import ugettext_lazy as _
from fluent_contents.models import ContentItem
from fluent_contents.plugins.text import appsettings
from django_wysiwyg.utils import clean_html, sanitize_html


class TextItem(ContentItem):
    """
    A snippet of HTML text to display on a page.
    """
    text = models.TextField(_('text'), blank=True)

    class Meta:
        verbose_name = _('Text item')
        verbose_name_plural = _('Text items')

    def save(self, *args, **kwargs):
        # Cleanup the HTML if requested
        if appsettings.FLUENT_TEXT_CLEAN_HTML:
            self.text = clean_html(self.text)
        if appsettings.FLUENT_TEXT_SANITIZE_HTML:
            self.text = sanitize_html(self.text)

        super(ContentItem, self).save(*args, **kwargs)
