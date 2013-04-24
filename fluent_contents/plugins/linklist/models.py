from django.db import models
from django.utils.translation import ugettext_lazy as _
from fluent_contents.extensions import OrderableModel, PluginUrlField
from fluent_contents.models import ContentItem


class LinkListItem(ContentItem):
    """
    An ``<iframe>`` that is displayed at the page..
    """
    title = models.CharField(_("Title"), max_length=200)

    class Meta:
        verbose_name = _("Link list")
        verbose_name_plural = _("Link lists")

    def __unicode__(self):
        return self.title


class Link(OrderableModel):
    """
    An individual link in the linklist.
    """
    linklist = models.ForeignKey(LinkListItem, related_name='links')
    title = models.CharField(_("Title"), max_length=200)
    url = PluginUrlField(_("Link"))

    class Meta:
        verbose_name = _("Link")
        verbose_name_plural = _("Links")

    def __unicode__(self):
        return self.title
