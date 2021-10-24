from django.core.exceptions import ValidationError
from django.db.models import URLField
from django.utils.translation import gettext_lazy as _

from fluent_contents.plugins.oembeditem import backend


class OEmbedUrlField(URLField):
    """
    URL Field which validates whether the URL is supported by the OEmbed provider.

    This feature is provided as model field, so other apps can use the same logic too.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault(
            "help_text",
            _(
                "Enter the URL of the online content to embed (e.g. a YouTube or Vimeo video, SlideShare presentation, etc..)"
            ),
        )
        super().__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        url = super().clean(*args, **kwargs)

        if not backend.has_provider_for_url(url):
            # It's also possible that the backend is configured as provider.
            raise ValidationError(_("The URL is not valid for embedding content"))

        return url
