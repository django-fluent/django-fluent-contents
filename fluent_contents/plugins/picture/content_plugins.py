
from django.contrib.admin.widgets import AdminTextareaWidget
from django.utils.translation import ugettext_lazy as _
from fluent_contents.extensions import ContentPlugin, plugin_pool
from fluent_contents.plugins.picture.models import PictureItem


@plugin_pool.register
class PicturePlugin(ContentPlugin):
    """
    Plugin for rendering pictures.
    """
    model = PictureItem
    category = _('Media')
    render_template = "fluent_contents/plugins/picture/default.html"

    formfield_overrides = {
        'caption': {
            'widget': AdminTextareaWidget(attrs={'cols': 30, 'rows': 4, 'class': 'vTextField'}),
        },
    }
    radio_fields = {
        'align': ContentPlugin.HORIZONTAL
    }

    class Media:
        css = {
            'screen': (
                'fluent_contents/plugins/picture/picture_admin.css',
            )
        }
