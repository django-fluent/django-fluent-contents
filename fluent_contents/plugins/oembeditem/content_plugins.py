"""
Definition of the plugin.
"""
from django.utils.translation import ugettext_lazy as _
from fluent_contents.extensions import ContentPlugin, plugin_pool
from fluent_contents.plugins.oembeditem.forms import OEmbedItemForm
from fluent_contents.plugins.oembeditem.models import OEmbedItem


@plugin_pool.register
class OEmbedPlugin(ContentPlugin):
    model = OEmbedItem
    category = _('Online content')
    form = OEmbedItemForm
    render_template = "fluent_contents/plugins/oembed/default.html"

    class Media:
        css = {
            'screen': (
                'fluent_contents/plugins/oembed/oembed_admin.css',
            )
        }


    def get_render_template(self, request, instance, **kwargs):
        """
        Allow to style the item based on the type.
        """
        return ["fluent_contents/plugins/oembed/{type}.html".format(type=instance.type or 'default'), self.render_template]
