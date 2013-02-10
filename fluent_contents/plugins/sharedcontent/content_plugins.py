from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from fluent_contents.extensions import ContentPlugin, plugin_pool
from fluent_contents.plugins.sharedcontent.models import SharedContentItem
from fluent_contents.rendering import render_placeholder


@plugin_pool.register
class SharedContentPlugin(ContentPlugin):
    """
    Plugin for sharing content at the page.
    """
    model = SharedContentItem
    category = _('Advanced')
    cache_output = False  # Individual items are cached, complete block not yet.

    def render(self, request, instance, **kwargs):
        # Not using "template" parameter yet.
        shared_content = instance.shared_content
        return mark_safe(render_placeholder(request, shared_content.contents, parent_object=shared_content))
