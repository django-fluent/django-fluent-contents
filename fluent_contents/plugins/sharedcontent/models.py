from django.conf import settings
from future.builtins import str
from future.utils import python_2_unicode_compatible
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _
from fluent_contents.models.mixins import CachedModelMixin
from fluent_contents.models import ContentItem, PlaceholderField, ContentItemRelation
from fluent_contents.plugins.sharedcontent.cache import get_shared_content_cache_key_ptr
from parler.models import TranslatableModel, TranslatedFields
from .managers import SharedContentManager
from .utils import get_current_site_id


@python_2_unicode_compatible
class SharedContent(CachedModelMixin, TranslatableModel):
    """
    The parent hosting object for shared content
    """
    translations = TranslatedFields(
        title = models.CharField(_("Title"), max_length=200)
    )

    parent_site = models.ForeignKey(Site, editable=False, default=get_current_site_id)
    slug = models.SlugField(_("Template code"), help_text=_("This unique name can be used refer to this content in in templates."))
    is_cross_site = models.BooleanField(_("Share between all sites"), blank=True, default=False,
        help_text=_("This allows contents can be shared between multiple sites in this project.<br>\n"
                    "Make sure that any URLs in the content work with all sites where the content is displayed."))

    contents = PlaceholderField("shared_content", verbose_name=_("Contents"))

    # NOTE: settings such as "template_name", and which plugins are allowed can be added later.

    # Adding the reverse relation for ContentItem objects
    # causes the admin to list the related objects when deleting this model.
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
        return self.safe_translation_getter('title', self.slug)

    def __init__(self, *args, **kwargs):
        super(SharedContent, self).__init__(*args, **kwargs)
        self._was_cross_site = self.is_cross_site
        self._old_slug = self.slug

    def get_cache_keys(self):
        # When the shared content is saved, make sure all rendering output PTRs are cleared.
        # The 'slug' could have changed. Whether the Placeholder output is cleared,
        # depends on whether those objects are altered too.
        if self.is_cross_site or self._was_cross_site:
            sites = list(Site.objects.all().values_list('pk', flat=True))
        else:
            sites = [self.parent_site_id]

        keys = []
        for site_id in sites:
            for language_code, _ in settings.LANGUAGES:
                keys.append(get_shared_content_cache_key_ptr(site_id, self._old_slug, language_code))
        return keys


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
