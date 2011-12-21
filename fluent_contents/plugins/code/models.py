from django.db import models
from django.utils.translation import ugettext_lazy as _
from fluent_contents.models import ContentItem
from fluent_contents.plugins.code import backend, appsettings

class CodeItem(ContentItem):
    """
    A snippet of source code, formatted with syntax highlighting.
    """

    language = models.CharField(_('Language'), max_length=50, choices=backend.LANGUAGE_CHOICES, default=appsettings.FLUENT_CODE_DEFAULT_LANGUAGE)
    code = models.TextField(_('Code'))
    linenumbers = models.BooleanField(_('Show line numbers'), default=appsettings.FLUENT_CODE_DEFAULT_LINE_NUMBERS)

    class Meta:
        verbose_name = _('Code snippet')
        verbose_name_plural = _('Code snippets')

    def __unicode__(self):
        return self.code
