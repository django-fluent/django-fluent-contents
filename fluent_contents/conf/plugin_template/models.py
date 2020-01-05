from django.db import models
from django.utils.translation import gettext_lazy as _

from fluent_contents.models import ContentItem


class {{ model }}(ContentItem):
    """
    CMS plugin data model to ...
    """
    title = models.CharField(_("Title"), max_length=200)

    class Meta:
        verbose_name = _("{{ model|title }}")
        verbose_name_plural = _("{{ model|title }}s")

    def __str__(self):
        return self.title
