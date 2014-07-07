from future.utils import python_2_unicode_compatible
from django.utils.html import strip_tags
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _
from fluent_contents.extensions import PluginHtmlField
from fluent_contents.models import ContentItem
from fluent_contents.plugins.text import appsettings
from django_wysiwyg.utils import clean_html, sanitize_html


@python_2_unicode_compatible
class TextItem(ContentItem):
    """
    A snippet of HTML text to display on a page.
    """
    text = PluginHtmlField(_('text'), blank=True)

    class Meta:
        verbose_name = _('Text')
        verbose_name_plural = _('Text')

    def __str__(self):
        return Truncator(strip_tags(self.text)).words(20)

    def save(self, *args, **kwargs):
        # Make well-formed if requested
        if appsettings.FLUENT_TEXT_CLEAN_HTML:
            self.text = clean_html(self.text)

        # Remove unwanted tags if requested
        if appsettings.FLUENT_TEXT_SANITIZE_HTML:
            self.text = sanitize_html(self.text)

        super(TextItem, self).save(*args, **kwargs)
