"""
Panels for django-debug-toolbar
"""
from datetime import timedelta
from debug_toolbar.utils import ThreadCollector
from debug_toolbar.panels import Panel
from django.utils.translation import ugettext_lazy as _

from fluent_contents.models import ContentItem
from fluent_contents.rendering.core import RenderingPipe, ResultTracker
from fluent_contents.rendering.utils import get_placeholder_debug_name

collector = ThreadCollector()


class DebugResultTracker(ResultTracker):
    """
    Hook into the rendering pipeline to receive updates
    """
    def __init__(self, *args, **kwargs):
        super(DebugResultTracker, self).__init__(*args, **kwargs)
        # Reference this result in the data collector.
        collector.collect(self)
        # Track that the object was never cachable
        self.initial_all_cachable = self.all_cacheable


class ContentPluginPanel(Panel):
    """
    Panel for debugging the rendering of content items.
    """
    nav_title = _("Content Items")
    template = "fluent_contents/debug_toolbar_panel.html"

    def __init__(self, toolbar):
        super(ContentPluginPanel, self).__init__(toolbar)

    def enable_instrumentation(self):
        # Patch the regular rendering to report to the debug toolbar
        RenderingPipe.result_class = DebugResultTracker

    def disable_instrumentation(self):
        # Restore original result tracker
        RenderingPipe.result_class = ResultTracker

    @property
    def title(self):
        return _("{0} content items rendered in {1} placeholders").format(self.num_items, self.num_placeholders)

    @property
    def nav_subtitle(self):
        return _("{0} items in {1} placeholders").format(self.num_items, self.num_placeholders)

    def process_response(self, request, response):
        # Serialize to dict to store as debug toolbar stats
        rendered_placeholders = []
        self.num_items = 0
        self.num_placeholders = 0
        for resulttracker in collector.get_collection():
            rendered_items = []
            retreived_items = set(item.pk for item in resulttracker.remaining_items)
            for contentitem, output in resulttracker.get_output(include_exceptions=True):
                plugin = contentitem.plugin
                is_cached = contentitem.pk not in retreived_items

                if contentitem.__class__ is ContentItem:
                    # Need to real item for get_render_template() but don't want to perform queries for this!
                    #contentitem = plugin.model.objects.get(pk=contentitem.pk)
                    templates = plugin.render_template
                    template_dummy = True
                else:
                    templates = plugin.get_render_template(request, contentitem)
                    template_dummy = False

                if templates is not None and not isinstance(templates, (list,tuple)):
                    templates = [templates]

                cache_timeout = None
                if output is ResultTracker.MISSING:
                    status = 'missing'
                elif output is ResultTracker.SKIPPED:
                    status = 'skipped'
                else:
                    if not is_cached:
                        status = 'fetched'
                        cache_timeout = output.cache_timeout
                    else:
                        status = 'cached'
                        cache_timeout = plugin.cache_timeout

                    cache_timeout = None if isinstance(cache_timeout, object) else int(cache_timeout)

                rendered_items.append({
                    'model': plugin.model.__name__,
                    'model_path': _full_python_path(contentitem.__class__),
                    'plugin': plugin.name,
                    'plugin_path': _full_python_path(plugin.__class__),
                    'pk': contentitem.pk,
                    'templates': templates,
                    'templates_dummy': template_dummy,
                    'status': status,
                    'cached': is_cached,
                    'cache_output': plugin.cache_output,
                    'cache_output_per_language': plugin.cache_output_per_language,
                    'cache_output_per_site': plugin.cache_output_per_site,
                    'cache_timeout': cache_timeout,
                    'cache_timeout_str': str(timedelta(seconds=cache_timeout)) if cache_timeout else None,
                })
                self.num_items += 1

            all_timeout = None if isinstance(resulttracker.all_timeout, object) else int(resulttracker.all_timeout)
            parent_object = resulttracker.parent_object
            rendered_placeholders.append({
                'parent_model': parent_object.__class__.__name__ if parent_object is not None else None,
                'parent_id': parent_object.pk if parent_object is not None else None,
                'slot': resulttracker.placeholder_name,
                'debug_name': _debug_name(resulttracker),
                'all_cachable': resulttracker.all_cacheable,
                'initial_all_cachable': resulttracker.initial_all_cachable,
                'all_timeout': all_timeout,
                'all_timeout_str': str(timedelta(seconds=all_timeout)) if all_timeout else None,
                'items': rendered_items,
            })
            self.num_placeholders += 1

        self.record_stats({
            'runs': rendered_placeholders,
        })

        collector.clear_collection()


def _full_python_path(cls):
    return "{0}.{1}".format(cls.__module__, cls.__name__)


def _debug_name(resulttracker):
    if resulttracker.placeholder_name == 'shared_content':
        return resulttracker.parent_object.slug
    else:
        return resulttracker.placeholder_name
