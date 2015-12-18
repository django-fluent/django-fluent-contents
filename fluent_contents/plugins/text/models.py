from django.db import models
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
    text_final = models.TextField(editable=False, blank=True, null=True)

    class Meta:
        verbose_name = _('Text')
        verbose_name_plural = _('Text')

    def __str__(self):
        return Truncator(strip_tags(self.text)).words(20)

    def save(self, *args, **kwargs):
        # Even through the form likely performed pre-processing already,
        # this makes sure that manual .save() calls also go through the same process.
        self.text = self.apply_pre_filters(self.text)

        # Perform post processing. This does not effect the original 'self.text'
        self.text_final = self.apply_post_filters(self.text)
        super(TextItem, self).save(*args, **kwargs)

    def apply_pre_filters(self, html):
        """
        Perform optimizations in the HTML source code.
        """
        # Make well-formed if requested
        if appsettings.FLUENT_TEXT_CLEAN_HTML:
            html = clean_html(html)

        # Remove unwanted tags if requested
        if appsettings.FLUENT_TEXT_SANITIZE_HTML:
            html = sanitize_html(html)

        # Allow pre processing. Typical use-case is HTML syntax correction.
        for post_func in appsettings.PRE_FILTER_FUNCTIONS:
            html = post_func(self, html)

        return html

    def apply_post_filters(self, html):
        """
        Allow post processing functions to change the text.
        This change is not saved in the original text.
        """
        for post_func in appsettings.POST_FILTER_FUNCTIONS:
            html = post_func(self, html)

        return html
