from fluent_contents.extensions import ContentPlugin, plugin_pool

from .models import {{ model }}


@plugin_pool.register
class {{ plugin }}(ContentPlugin):
    """
    CMS plugin for ...
    """
    model = {{ model }}
    #category = ContentPlugin.ADVANCED
    render_template = "includes/fluentcms_plugins/{{ app_name }}.html"
