"""
Form designer link plugin.

This plugin displays a form at the page, that was created with form_designer.
To customize the output, configure the ``django-form-designer`` application via the settings file.
For example, use:

 * ``FORM_DESIGNER_DEFAULT_FORM_TEMPLATE`` or ``FORM_TEMPLATES`` to control the form output (e.g. render it with ``django-uni-form``).
 * ``FORM_DESIGNER_FIELD_CLASSES`` to define which field types are allowed.
 * ``FORM_DESIGNER_WIDGET_CLASSES`` to define which widgets are allowed.
"""
from django.utils.translation import ugettext_lazy as _
from fluent_contents.extensions import ContentPlugin, plugin_pool
from fluent_contents.plugins.formdesignerlink.models import FormDesignerLink
from form_designer import settings as form_designer_settings
from form_designer.views import process_form


@plugin_pool.register
class FormDesignerLinkPlugin(ContentPlugin):
    model = FormDesignerLink
    category = _('Interactivity')
    cache_output = False


    def get_render_template(self, request, instance, **kwargs):
        return instance.form_definition.form_template_name or self.render_template or form_designer_settings.DEFAULT_FORM_TEMPLATE


    def get_context(self, request, instance, **kwargs):
        context = {}
        # The process_form() function is designed with Django CMS in mind,
        # and responds to both the GET and POST request.
        return process_form(request, instance.form_definition, context, is_cms_plugin=True)


