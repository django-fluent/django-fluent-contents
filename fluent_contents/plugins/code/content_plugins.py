"""
Definition of the plugin.
"""
from django.utils.safestring import mark_safe
from fluent_contents.extensions import ContentPlugin, plugin_pool
from fluent_contents.plugins.code.models import CodeItem
from fluent_contents.plugins.code import appsettings, backend


@plugin_pool.register
class CodePlugin(ContentPlugin):
    model = CodeItem
    category = ContentPlugin.PROGRAMMING
    admin_form_template = "admin/fluent_contents/plugins/code/admin_form.html"
    render_template = "fluent_contents/plugins/code/code.html"

    class Media:
        css = {'screen': ('fluent_contents/code/code_admin.css',)}

    def get_context(self, request, instance, **kwargs):
        # Style is not stored in the model,
        # it needs to be a side-wide setting (maybe even in the theme)
        code = mark_safe(backend.render_code(instance, style_name=appsettings.FLUENT_CODE_STYLE))

        context = super(CodePlugin, self).get_context(request, instance, **kwargs)
        context.update({
            'code': code,
        })
        return context
