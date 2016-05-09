import django
from django.core.exceptions import ValidationError
from django.db.models import URLField
from django.utils.translation import ugettext_lazy as _
from fluent_contents.plugins.oembeditem import backend


class OEmbedUrlField(URLField):
    """
    URL Field which validates whether the URL is supported by the OEmbed provider.

    This feature is provided as model field, so other apps can use the same logic too.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('help_text', _("Enter the URL of the online content to embed (e.g. a YouTube or Vimeo video, SlideShare presentation, etc..)"))
        super(OEmbedUrlField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        url = super(OEmbedUrlField, self).clean(*args, **kwargs)

        if not backend.has_provider_for_url(url):
            raise ValidationError(_("The URL is not valid for embedding content"))  # or is not configured as provider.

        return url


if django.VERSION < (1, 7):
    try:
        from south.modelsinspector import add_introspection_rules
    except ImportError:
        pass
    else:
        add_introspection_rules([], ["^" + __name__.replace(".", "\.") + "\.OEmbedUrlField"])
