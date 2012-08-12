from django.db import models
from django.utils.translation import ugettext_lazy as _
from fluent_contents.models.db import ContentItem
from fluent_contents.plugins.oembeditem import backend

class OEmbedItem(ContentItem):
    """
    Embedded media via OEmbed
    """
    TYPE_PHOTO = 'photo'
    TYPE_VIDEO = 'video'
    TYPE_RICH = 'rich'  # HTML
    TYPE_LINK = 'link'

    # Fetch parameters
    embed_url = models.URLField(_("URL to embed"), help_text=_("Enter the URL of the online content to embed (e.g. a YouTube or Vimeo video, SlideShare presentation, etc..)"))
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


    class Meta:
        verbose_name = _("Embedded media")
        verbose_name_plural = _("Embeddded media")


    def __unicode__(self):
        return self.title or self.embed_url


    def __init__(self, *args, **kwargs):
        super(OEmbedItem, self).__init__(*args, **kwargs)
        self._old_embed_url = self.embed_url


    def save(self, *args, **kwargs):
        self.update_oembed_data()
        super(OEmbedItem, self).save(*args, **kwargs)


    def update_oembed_data(self):
        if not self.type or self._old_embed_url != self.embed_url:
            response = backend.get_oembed_data(self.embed_url, self.embed_max_width, self.embed_max_height)
            self.store_response(response)
            self._old_embed_url = self.embed_url


    def store_response(self, response):
        # Store the OEmbed response
        # Unused: cache_age
        # Security considerations: URLs are checked by Django for http:// or ftp://
        KEYS = (
            'type', 'title', 'description', 'author_name', 'author_url', 'provider_url', 'provider_name',
            'thumbnail_width', 'thumbnail_height', 'thumbnail_url', 'height', 'width', 'html', 'url'
        )

        for key in KEYS:
            if response.has_key(key):
                setattr(self, key, response[key])
