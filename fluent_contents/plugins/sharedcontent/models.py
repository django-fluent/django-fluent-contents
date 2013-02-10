from django.db import models
from django.utils.translation import ugettext_lazy as _
from fluent_contents.models import ContentItem, PlaceholderField


class SharedContent(models.Model):
    """
    The parent hosting object for shared content
    """
    title = models.CharField(_("Title"), max_length=200)
    slug = models.SlugField(_("Template code"), unique=True, help_text=_("This unique name can be used refer to this content in in templates."))
    contents = PlaceholderField("shared_content", verbose_name=_("Contents"))

    # NOTE: settings such as "template_name", and which plugins are allowed can be added later.

    class Meta:
        verbose_name = _("Shared content")
        verbose_name_plural = _("Shared content")

    def __unicode__(self):
        return self.title


class SharedContentItem(ContentItem):
    """
    The contentitem to include in a page.
    """
    shared_content = models.ForeignKey(SharedContent, verbose_name=_('Shared content'), related_name='shared_content_items')

    class Meta:
        verbose_name = _('Shared content item')
        verbose_name_plural = _('Shared content items')

    def __unicode__(self):
        return unicode(self.shared_content)
