import logging
import six
from future.builtins import str
from django.conf import settings
from django.forms import Media
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.utils.html import escape
from django.utils.safestring import mark_safe
from parler.utils.context import smart_override
from fluent_contents import appsettings
from fluent_contents.cache import get_rendering_cache_key
from fluent_contents.extensions import PluginNotFound
from fluent_contents.models import ContentItemOutput, DEFAULT_TIMEOUT
from . import markers
from .utils import optimize_logger_level, get_placeholder_debug_name, add_media, get_render_language, is_template_updated

logger = logging.getLogger('fluent_contents.rendering')


class ResultTracker(object):
    """
    A tracking of intermediate results during rendering.
    This object is completely agnostic to what is's rendering,
    it just stores "output" for a "contentitem".
    """
    MISSING = object()
    SKIPPED = object()

    def __init__(self, placeholder, items):
        # The source
        self.placeholder = placeholder
        self.items = items

        # The results
        self.all_timeout = DEFAULT_TIMEOUT
        self.all_cacheable = True
        self.output_ordering = []
        self.remaining_items = []
        self.item_output = {}

        # Other state fields
        self.placeholder_name = '@global@' if placeholder is None else placeholder.slot

    def add_output(self, contentitem, output):
        """
        Track the output of a given content item.
        :type contentitem: ContentItem
        :type output: O
        """
        # Using index by pk, because contentitem could be a derived or base instance.
        item_id = contentitem.pk or id(contentitem)
        self.item_output[item_id] = output

    def add_remaining(self, contentitem):
        """Track that an item is not rendered yet, and needs to be processed later."""
        self.remaining_items.append(contentitem)

    def add_remaining_list(self, contentitems):
        # Adding a list of items, not a queryset. Items might be created on the fly (no .pk).
        self.remaining_items.extend(contentitems)
        self.output_ordering.extend(item.pk or id(item) for item in contentitems)

    def fetch_remaining_instances(self, queryset):
        """Read the derived table data for all objects tracked as remaining (=not found in the cache)."""
        if self.remaining_items:
            self.remaining_items = queryset.get_real_instances(self.remaining_items)

    def add_plugin_timeout(self, plugin):
        self.all_timeout = _min_timeout(self.all_timeout, plugin.cache_timeout)

    def set_uncachable(self):
        """Set that it can't cache all items as a single entry."""
        self.all_cacheable = False

    def get_output(self):
        """
        Return the output in the correct ordering.
        :rtype: list[Tuple[int, O]]
        """
        # Order all rendered items in the correct sequence.  The derived tables could be truncated/reset,
        # so the base class model indexes don't necessary match with the derived indexes. Hence the dict + KeyError handling.
        ordered_output = []
        for pk in self.output_ordering:
            try:
                output = self.item_output[pk]
            except KeyError:
                # The item was not rendered!
                output = self.MISSING
            ordered_output.append((pk, output))

        return ordered_output


class RenderingPipe(object):
    """
    The rendering happens using this class to keep it slightly easier to extend
    and break the rendering into more managable pieces.

    The rendering happens in these parts:

    - incoming ContentItem objects are read as base class only (using ``.non_polymorphic()``)
    - the cache is checked for any existing items.
    - remaining items are queried for their derived class.
    - rendered items are cached whenever possible.
    - all output is merged and combined.
    """
    #: The class which stores intermediate results
    result_class = ResultTracker

    def __init__(self, request, edit_mode=None):
        if edit_mode is None:
            edit_mode = markers.is_edit_mode(request)

        self.request = request
        self.edit_mode = edit_mode
        optimize_logger_level(logger, logging.DEBUG)

    def render_items(self, placeholder, items, parent_object=None, template_name=None, cachable=False):
        """
        The main rendering sequence.
        """
        # Variables filled during rendering:
        result = self.result_class(placeholder, items)
        if self.edit_mode:
            result.set_uncachable()

        if not hasattr(items, "non_polymorphic"):
            # The items is either a list of manually created items, or it's a QuerySet.
            # Can't prevent reading the subclasses only, so don't bother with caching here.
            result.add_remaining_list(items)
        else:
            # Unless it was done before, disable polymorphic effects.
            if not items.polymorphic_disabled:
                items = items.non_polymorphic()

            self._fetch_cached_output(items, result=result)
            result.fetch_remaining_instances(queryset=items)

        # See if the queryset contained anything.
        # This test is moved here, to prevent earlier query execution.
        if not items:
            logger.debug("- no items in placeholder '%s'", get_placeholder_debug_name(placeholder))
            return ContentItemOutput(mark_safe(u"<!-- no items in placeholder '{0}' -->".format(escape(result.placeholder_name))))

        # Start the actual rendering of remaining items.
        if result.remaining_items:
            self._render_uncached_items(result.remaining_items, result=result)

        # And merge all items together.
        return self._merge_output(result, items, parent_object, template_name, cachable)

    def _fetch_cached_output(self, items, result):
        """
        First try to fetch all items from the cache.
        The items are 'non-polymorphic', so only point to their base class.
        If these are found, there is no need to query the derived data from the database.
        """
        if not appsettings.FLUENT_CONTENTS_CACHE_OUTPUT:
            result.add_remaining_list(items)
            return

        for contentitem in items:
            result.output_ordering.append(contentitem.pk)
            output = None

            try:
                plugin = contentitem.plugin
            except PluginNotFound as ex:
                result.add_output(contentitem, ex)  # Will deal with that later.
                logger.debug("- item #%s has no matching plugin: %s", contentitem.pk, str(ex))
                continue

            # Respect the cache output setting of the plugin
            if plugin.cache_output and contentitem.pk:
                result.add_plugin_timeout(plugin)
                output = plugin.get_cached_output(result.placeholder_name, contentitem)

                # Support transition to new output format.
                if output is not None and not isinstance(output, ContentItemOutput):
                    output = None
                    logger.debug("Flushed cached output of {0}#{1} to store new ContentItemOutput format (key: {2})".format(plugin.type_name, contentitem.pk, placeholder_cache_name))

            # For debugging, ignore cached values when the template is updated.
            if output and settings.DEBUG:
                cachekey = get_rendering_cache_key(result.placeholder_name, contentitem)
                if settings.DEBUG and is_template_updated(self.request, contentitem, cachekey):
                    output = None

            if output:
                result.add_output(contentitem, output)
            else:
                result.add_remaining(contentitem)

    def _render_uncached_items(self, items, result):
        """
        Render a list of items, that didn't exist in the cache yet.
        """
        for contentitem in items:
            try:
                plugin = contentitem.plugin
            except PluginNotFound as ex:
                result.add_output(contentitem, ex)
                logger.debug("- item #%s has no matching plugin: %s", contentitem.pk, str(ex))
                continue

            render_language = get_render_language(contentitem)
            with smart_override(render_language):
                # Plugin output is likely HTML, but it should be placed in mark_safe() to raise awareness about escaping.
                # This is just like Django's Input.render() and unlike Node.render().
                output = plugin._render_contentitem(self.request, contentitem)

            # Try caching it.
            self._try_cache_output(plugin, contentitem, output, result=result)
            if self.edit_mode:
                output.html = markers.wrap_contentitem_output(output.html, contentitem)

            result.add_output(contentitem, output)

    def _try_cache_output(self, plugin, contentitem, output, result):
        if self._is_cachable(plugin, contentitem, output):
            # Cache the output
            contentitem.plugin.set_cached_output(result.placeholder_name, contentitem, output)
        else:
            # Item blocks caching the complete placeholder.
            result.set_uncachable()
            if appsettings.FLUENT_CONTENTS_CACHE_OUTPUT:
                logger.debug("- item #%s is NOT cachable! Prevented by %r", contentitem.pk, contentitem.plugin)

    @staticmethod
    def _is_cachable(plugin, contentitem, output):
         return appsettings.FLUENT_CONTENTS_CACHE_OUTPUT \
                and plugin.cache_output \
                and output.cacheable \
                and contentitem.pk

    def _merge_output(self, result, items, parent_object, template_name, cachable):
        """
        Combine all rendered items. Allow rendering the items with a template,
        to inserting separators or nice start/end code.
        """
        html_output, media = self._get_html_output(result, items)

        if not template_name:
            merged_html = mark_safe(u''.join(html_output))
        else:
            context = {
                'contentitems': list(zip(items, html_output)),
                'parent_object': parent_object,  # Can be None
                'edit_mode': self.edit_mode,
            }
            merged_html = render_to_string(template_name, context, context_instance=RequestContext(self.request))

            # By default, cachable is False for templates.
            # Template name is ambiguous, can't reliable expire.
            # Nor can be determined whether the template is consistent or not cacheable.
            if not cachable:
                result.set_uncachable()

        return ContentItemOutput(merged_html, media, cacheable=result.all_cacheable, cache_timeout=result.all_timeout)

    def _get_html_output(self, result, items):
        """
        Collect all HTML from the rendered items, in the correct ordering.
        The media is also collected in the same ordering, in case it's handled by django-compressor for example.
        """
        html_output = []
        merged_media = Media()
        for pk, output in result.get_output():
            if output is ResultTracker.MISSING:
                # Likely get_real_instances() didn't return an item for it.
                # The get_real_instances() didn't return an item for the derived table. This happens when either:
                # 1. that table is truncated/reset, while there is still an entry in the base ContentItem table.
                #    A query at the derived table happens every time the page is being rendered.
                # 2. the model was completely removed which means there is also a stale ContentType object.
                class_name = _get_stale_item_class_name(items, pk)
                html_output.append(u"<!-- Missing derived model for ContentItem #{id}: {cls}. -->\n".format(id=pk, cls=class_name))
                logger.warning("Missing derived model for ContentItem #{id}: {cls}.".format(id=pk, cls=class_name))
            elif isinstance(output, Exception):
                html_output.append(u'<!-- error: {0} -->\n'.format(str(output)))
            else:
                html_output.append(output.html)
                add_media(merged_media, output.media)

        return html_output, merged_media


def _get_stale_item_class_name(items, pk):
    item = next(item for item in items if item.pk == pk)
    try:
        return item.plugin.type_name
    except PluginNotFound:
        # Derived table isn't there because the model has been removed.
        # There is a stale ContentType object, no plugin associated or loaded.
        return 'content type is stale'


def _min_timeout(val1, val2):
    # Avoid min(int, object). That may work but it's
    # a CPython implementation detail to compare that as "int" < "object"
    if not isinstance(val2, six.integer_types):
        return val1

    if not isinstance(val1, six.integer_types):
        return val2

    return min(val1, val2)
