"""
Form designer link plugin.

This plugin displays a form at the page, that was created with form_designer.
To customize the output, configure the ``django-form-designer-ai`` application via the settings file.
For example, use:

 * ``FORM_DESIGNER_DEFAULT_FORM_TEMPLATE`` or ``FORM_TEMPLATES`` to control the form output (e.g. render it with ``django-uni-form``).
 * ``FORM_DESIGNER_FIELD_CLASSES`` to define which field types are allowed.
 * ``FORM_DESIGNER_WIDGET_CLASSES`` to define which widgets are allowed.
"""
from django.contrib.messages.api import get_messages
from form_designer import settings as form_designer_settings
from form_designer.views import process_form

from fluent_contents.extensions import ContentPlugin, plugin_pool
from fluent_contents.plugins.formdesignerlink.models import FormDesignerLink


@plugin_pool.register
class FormDesignerLinkPlugin(ContentPlugin):
    model = FormDesignerLink
    category = ContentPlugin.INTERACTIVITY
    cache_output = False

    def get_render_template(self, request, instance, **kwargs):
        # Overwritten to return a template from the instance.
        return (
            instance.form_definition.form_template_name
            or self.render_template
            or form_designer_settings.DEFAULT_FORM_TEMPLATE
        )

    def render(self, request, instance, **kwargs):
        # While overwriting get_context() would be sufficient here, this is rather easier to understand.
        # Implemented a custom rendering function instead.

        # The process_form() function is designed with Django CMS in mind,
        # and responds to both the GET and POST request.
        context = process_form(request, instance.form_definition, {}, disable_redirection=True)
        # Add no matter what, because the template needs it.
        context["messages"] = get_messages(request)

        # Render the plugin
        render_template = self.get_render_template(request, instance, **kwargs)
        return self.render_to_string(request, render_template, context)
