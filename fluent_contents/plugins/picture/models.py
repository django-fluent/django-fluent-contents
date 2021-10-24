from django.db import models
from django.utils.translation import gettext_lazy as _

from fluent_contents.extensions import PluginImageField, PluginUrlField
from fluent_contents.models import ContentItemManager
from fluent_contents.models.db import ContentItem

from . import appsettings


class PictureItem(ContentItem):
    """
    Display a picture
    """

    ALIGN_LEFT = "left"
    ALIGN_CENTER = "center"
    ALIGN_RIGHT = "right"
    ALIGN_CHOICES = (
        (ALIGN_LEFT, _("Left")),
        (ALIGN_CENTER, _("Center")),
        (ALIGN_RIGHT, _("Right")),
    )

    image = PluginImageField(_("Image"), upload_to=appsettings.FLUENT_PICTURE_UPLOAD_TO)
    caption = models.TextField(_("Caption"), blank=True)
    align = models.CharField(_("Align"), max_length=10, choices=ALIGN_CHOICES, blank=True)
    url = PluginUrlField(_("URL"), blank=True)
    in_new_window = models.BooleanField(_("Open in a new window"), default=False, blank=True)

    objects = ContentItemManager()  # Avoid Django 1.10 migrations

    class Meta:
        verbose_name = _("Picture")
        verbose_name_plural = _("Pictures")

    def __str__(self):
        return self.caption or str(self.image)

    @property
    def align_class(self):
        """
        The CSS class for alignment.
        """
        if self.align == self.ALIGN_LEFT:
            return "align-left"
        elif self.align == self.ALIGN_CENTER:
            return "align-center"
        elif self.align == self.ALIGN_RIGHT:
            return "align-right"
        else:
            return ""
