from django.conf import settings
from future.builtins import str
from future.utils import python_2_unicode_compatible
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields
from fluent_contents.models import ContentItem, PlaceholderField, ContentItemRelation
from .managers import SharedContentManager


def _get_current_site():
    return Site.objects.get_current()


@python_2_unicode_compatible
class SharedContent(TranslatableModel):
    """
    The parent hosting object for shared content
    """
    translations = TranslatedFields(
        title = models.CharField(_("Title"), max_length=200)
    )

    parent_site = models.ForeignKey(Site, editable=False, default=int(settings.SITE_ID))
    slug = models.SlugField(_("Template code"), help_text=_("This unique name can be used refer to this content in in templates."))
    is_cross_site = models.BooleanField(_("Share between all sites"), blank=True, default=False,
        help_text=_("This allows contents can be shared between multiple sites in this project.<br>\n"
                    "Make sure that any URLs in the content work with all sites where the content is displayed."))

    contents = PlaceholderField("shared_content", verbose_name=_("Contents"))

    # NOTE: settings such as "template_name", and which plugins are allowed can be added later.

    # Adding the reverse relation for ContentItem objects
    # causes the admin to list these objects when moving the shared content
    contentitem_set = ContentItemRelation()

    objects = SharedContentManager()

    class Meta:
        verbose_name = _("Shared content")
        verbose_name_plural = _("Shared content")
        unique_together = (
            ('parent_site', 'slug'),
        )
        ordering = ('slug',)

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class SharedContentItem(ContentItem):
    """
    The contentitem to include in a page.
    """
    shared_content = models.ForeignKey(SharedContent, verbose_name=_('Shared content'), related_name='shared_content_items')

    class Meta:
        verbose_name = _('Shared content')
        verbose_name_plural = _('Shared content')

    def __str__(self):
        return str(self.shared_content)
