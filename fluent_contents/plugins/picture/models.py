from any_imagefield.models import AnyImageField
from any_urlfield.models import AnyUrlField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from fluent_contents.models.db import ContentItem


class PictureItem(ContentItem):
    """
    Display a picture
    """
    ALIGN_LEFT = 'left'
    ALIGN_CENTER = 'center'
    ALIGN_RIGHT = 'right'
    ALIGN_CHOICES = (
        (ALIGN_LEFT, _("Left")),
        (ALIGN_CENTER, _("Center")),
        (ALIGN_RIGHT, _("Right")),
    )

    image = AnyImageField(_("Image"))
    caption = models.TextField(_("Caption"), blank=True)
    align = models.CharField(_("Align"), max_length=10, choices=ALIGN_CHOICES, blank=True)
    url = AnyUrlField(_("URL"), blank=True)

    class Meta:
        verbose_name = _("Picture")
        verbose_name_plural = _("Pictures")

    def __unicode__(self):
        return self.caption or unicode(self.image)

    @property
    def align_class(self):
        """
        The CSS class for alignment.
        """
        if self.align == self.ALIGN_LEFT:
            return 'align-left'
        elif self.align == self.ALIGN_CENTER:
            return 'align-center'
        elif self.align == self.ALIGN_RIGHT:
            return 'align-right'
        else:
            return ''
