from __future__ import unicode_literals
from future.utils import python_2_unicode_compatible
from django.db import models
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _
from fluent_contents.models import ContentItem, ContentItemManager
from fluent_contents.plugins.code import backend, appsettings
from fluent_utils.dry.fields import HideChoicesCharField


@python_2_unicode_compatible
class CodeItem(ContentItem):
    """
    A snippet of source code, formatted with syntax highlighting.
    """

    language = HideChoicesCharField(_('Language'), max_length=50, choices=backend.LANGUAGE_CHOICES, default=appsettings.FLUENT_CODE_DEFAULT_LANGUAGE)
    code = models.TextField(_('Code'))
    linenumbers = models.BooleanField(_('Show line numbers'), default=appsettings.FLUENT_CODE_DEFAULT_LINE_NUMBERS)

    objects = ContentItemManager()  # Avoid Django 1.10 migrations

    class Meta:
        verbose_name = _('Code snippet')
        verbose_name_plural = _('Code snippets')

    def __str__(self):
        return Truncator(self.code).words(20)
