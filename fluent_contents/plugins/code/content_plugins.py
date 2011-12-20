"""
Definition of the plugin.
"""
from django.utils.translation import ugettext_lazy as _
from fluent_contents.extensions import ContentPlugin, plugin_pool
from fluent_contents.plugins.code.models import CodeItem
from fluent_contents.plugins.code import appsettings, backend


class EcmsCodePlugin(ContentPlugin):
    model = CodeItem
    category = _('Programming')
    admin_form_template = "admin/fluent_contents/plugins/code/admin_form.html"

    class Media:
        css = {'screen': ('fluent_contents/code/code_admin.css',)}


    def render(self, instance, request, **kwargs):
        # Style is not stored in the model,
        # it needs to be a side-wide setting (maybe even in the theme)
        return backend.render_code(instance, style_name=appsettings.FLUENT_CODE_STYLE)


plugin_pool.register(EcmsCodePlugin)
