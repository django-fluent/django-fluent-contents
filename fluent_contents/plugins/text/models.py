from django.db import models
from future.utils import python_2_unicode_compatible
from django.utils.html import strip_tags
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _
from fluent_contents.extensions import PluginHtmlField
from fluent_contents.models import ContentItem
from fluent_contents.utils.filters import apply_filters


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

    def full_clean(self, *args, **kwargs):
        # This is called by the form when all values are assigned.
        # The pre filters are applied here, so any errors also appear as ValidationError.
        super(TextItem, self).full_clean(*args, **kwargs)

        self.text, self.text_final = apply_filters(self, self.text, field_name='text')
        if self.text_final == self.text:
            # No need to store duplicate content:
            self.text_final = None
