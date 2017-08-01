from future.builtins import str
from future.utils import python_2_unicode_compatible
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from micawber import ProviderException

from fluent_contents.models import ContentItemManager
from fluent_contents.models.db import ContentItem
from fluent_contents.plugins.oembeditem.fields import OEmbedUrlField
from fluent_contents.plugins.oembeditem import backend, appsettings


@python_2_unicode_compatible
class AbstractOEmbedItem(ContentItem):
    """
    The base class for an OEmbedItem,
    This allows to create custom models easily.

    .. versionadded:: 1.0
    """
    TYPE_PHOTO = 'photo'
    TYPE_VIDEO = 'video'
    TYPE_RICH = 'rich'  # HTML
    TYPE_LINK = 'link'

    # Fetch parameters
    embed_url = OEmbedUrlField(_("URL to embed"))
    embed_max_width = models.PositiveIntegerField(_("Max width"), blank=True, null=True)
    embed_max_height = models.PositiveIntegerField(_("Max height"), blank=True, null=True)

    # The cached response:
    type = models.CharField(editable=False, max_length=20, null=True, blank=True)
    url = models.URLField(editable=False, null=True, blank=True)
    title = models.CharField(editable=False, max_length=512, null=True, blank=True)
    description = models.TextField(editable=False, null=True, blank=True)

    author_name = models.CharField(editable=False, max_length=255, null=True, blank=True)
    author_url = models.URLField(editable=False, null=True, blank=True)
    provider_name = models.CharField(editable=False, max_length=255, null=True, blank=True)
    provider_url = models.URLField(editable=False, null=True, blank=True)

    thumbnail_url = models.URLField(editable=False, null=True, blank=True)
    thumbnail_height = models.IntegerField(editable=False, null=True, blank=True)
    thumbnail_width = models.IntegerField(editable=False, null=True, blank=True)

    height = models.IntegerField(editable=False, null=True, blank=True)
    width = models.IntegerField(editable=False, null=True, blank=True)
    html = models.TextField(editable=False, null=True, blank=True)

    objects = ContentItemManager()  # Avoid Django 1.10 migrations

    class Meta:
        abstract = True
        verbose_name = _("Online media")
        verbose_name_plural = _("Online media")

    def __str__(self):
        return self.title or self.embed_url

    def __init__(self, *args, **kwargs):
        super(AbstractOEmbedItem, self).__init__(*args, **kwargs)
        self._old_embed_url = self.embed_url
        self._old_embed_max_width = self.embed_max_width
        self._old_embed_max_height = self.embed_max_height

    def save(self, *args, **kwargs):
        self.update_oembed_data()  # if clean() did not run, still update the oembed
        super(AbstractOEmbedItem, self).save(*args, **kwargs)

    def clean(self):
        # Avoid getting server errors when the URL is not valid.
        try:
            self.update_oembed_data()
        except ProviderException as e:
            raise ValidationError(str(e))

    def update_oembed_data(self, force=False, **backend_params):
        """
        Update the OEmbeddata if needed.

        .. versionadded:: 1.0 Added force and backend_params parameters.
        """
        if appsettings.FLUENT_OEMBED_FORCE_HTTPS and self.embed_url.startswith('http://'):
            self.embed_url = 'https://' + self.embed_url[7:]

        if force or self._input_changed():
            # Fetch new embed code
            params = self.get_oembed_params(self.embed_url)
            params.update(backend_params)
            response = backend.get_oembed_data(self.embed_url, **params)

            # Save it
            self.store_response(response)

            # Track field changes
            self._old_embed_url = self.embed_url
            self._old_embed_max_width = self.embed_max_width
            self._old_embed_max_height = self.embed_max_height

    def get_oembed_params(self, embed_url):
        """
        .. versionadded:: 1.0

           Allow to define the parameters that are passed to the backend to fetch the current URL.
        """
        return {
            'max_width': self.embed_max_width,
            'max_height': self.embed_max_height,
        }

    def _input_changed(self):
        return not self.type \
            or self._old_embed_url != self.embed_url \
            or self._old_embed_max_width != self.embed_max_width \
            or self._old_embed_max_height != self.embed_max_height

    def store_response(self, response):
        # Store the OEmbed response
        # Unused: cache_age
        # Security considerations: URLs are checked by Django for http:// or ftp://
        KEYS = (
            'type', 'title', 'description', 'author_name', 'author_url', 'provider_url', 'provider_name',
            'thumbnail_width', 'thumbnail_height', 'thumbnail_url', 'height', 'width', 'html', 'url'
        )

        for key in KEYS:
            if key in response:
                setattr(self, key, response[key])


class OEmbedItem(AbstractOEmbedItem):
    """
    Embedded media via OEmbed
    """

    objects = ContentItemManager()  # Avoid Django 1.10 migrations

    class Meta:
        verbose_name = _("Online media")
        verbose_name_plural = _("Online media")
