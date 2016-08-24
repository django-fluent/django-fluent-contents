from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.six import python_2_unicode_compatible
from fluent_contents.models import ContentItem


@python_2_unicode_compatible
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
