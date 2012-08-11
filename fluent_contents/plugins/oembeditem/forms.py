from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from fluent_contents.forms import ContentItemForm
from fluent_contents.plugins.oembeditem import backend


class OEmbedItemForm(ContentItemForm):
    def clean_embed_url(self):
        """
        Validate the URL
        """
        url = self.cleaned_data['embed_url']
        if not backend.has_provider_for_url(url):
            raise ValidationError(_("The URL is not valid for embedding content"))  # or is not configured as provider.

        return url
