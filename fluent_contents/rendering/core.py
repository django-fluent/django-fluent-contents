import logging
import six
from future.builtins import str
from django.core.cache import cache
from django.conf import settings
from django.forms import Media
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.utils.html import escape
from django.utils.safestring import mark_safe
from parler.utils.context import smart_override
from fluent_utils.django_compat import is_queryset_empty
from fluent_contents import appsettings
from fluent_contents.cache import get_rendering_cache_key, get_placeholder_cache_key_for_parent
from fluent_contents.extensions import PluginNotFound
from fluent_contents.models import ContentItemOutput, DEFAULT_TIMEOUT, get_parent_language_code
from . import markers
from .utils import optimize_logger_level, get_placeholder_debug_name, add_media, get_render_language, is_template_updated

logger = logging.getLogger('fluent_contents.rendering')


def get_placeholder_name(placeholder):
    # This check likely be removed, but keep for backwards compatibility.
    return '@global@' if placeholder is None else placeholder.slot


class ResultTracker(object):
    """
    A tracking of intermediate results during rendering.
    This object is completely agnostic to what is's rendering,
    it just stores "output" for a "contentitem".
    """
    MISSING = object()
    SKIPPED = object()

    def __init__(self, request, parent_object, placeholder, items, all_cacheable=True):
        # The source
        self.request = request
        self.parent_object = parent_object
        self.placeholder = placeholder
        self.items = items

        # The results
        self.all_timeout = DEFAULT_TIMEOUT
        self.all_cacheable = all_cacheable
        self.output_ordering = []
        self.remaining_items = []
        self.item_output = {}
        self.item_source = {}  # for debugging

        # Other state fields
        self.placeholder_name = get_placeholder_name(placeholder)

    def store_output(self, contentitem, output):
        """
        Track the output of a given content item.
        :type contentitem: ContentItem
        :type output: O
        """
        self._set_output(contentitem, output)

    def store_exception(self, contentitem, exception):
        # Track exceptions.
        # Currently done in self.item_output, but avoid the store_output() call,
        # so this implementation detail is hidden from code that overrides store_output()
        self._set_output(contentitem, exception)

    def set_skipped(self, contentitem):
        # See store_exception() for this logic.
        self._set_output(contentitem, self.SKIPPED)

    def _set_output(self, contentitem, output):
        # Using index by pk, because contentitem could be a derived or base instance.
        item_id = self._get_item_id(contentitem)
        self.item_output[item_id] = output
        self.item_source[item_id] = contentitem

    def _get_item_id(self, contentitem):
        return contentitem.pk or id(contentitem)

    def add_ordering(self, contentitem):
        item_id = self._get_item_id(contentitem)
        self.item_source[item_id] = contentitem
        self.output_ordering.append(item_id)

    def add_remaining(self, contentitem):
        """Track that an item is not rendered yet, and needs to be processed later."""
        self.remaining_items.append(contentitem)

    def add_remaining_list(self, contentitems):
        # Adding a list of items, not a queryset. Items might be created on the fly (no .pk).
        self.remaining_items.extend(contentitems)
        self.output_ordering.extend(self._get_item_id(item) for item in contentitems)

    def fetch_remaining_instances(self, queryset):
        """Read the derived table data for all objects tracked as remaining (=not found in the cache)."""
        if self.remaining_items:
            self.remaining_items = queryset.get_real_instances(self.remaining_items)

    def add_plugin_timeout(self, plugin):
        self.all_timeout = _min_timeout(self.all_timeout, plugin.cache_timeout)

    def set_uncachable(self):
        """Set that it can't cache all items as a single entry."""
        self.all_cacheable = False

    def get_output(self, include_exceptions=False):
        """
        Return the output in the correct ordering.
        :rtype: list[Tuple[contentitem, O]]
        """
        # Order all rendered items in the correct sequence.
        # Don't assume the derived tables are in perfect shape, hence the dict + KeyError handling.
        # The derived tables could be truncated/reset or store_output() could be omitted.
        ordered_output = []
        for item_id in self.output_ordering:
            contentitem = self.item_source[item_id]
            try:
                output = self.item_output[item_id]
            except KeyError:
                # The item was not rendered!
                if not include_exceptions:
                    continue

                output = self.MISSING
            else:
                # Filter exceptions out.
                if not include_exceptions:
                    if isinstance(output, Exception) or output is self.SKIPPED:
                        continue

            ordered_output.append((contentitem, output))

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

    #: Tell whether the cache can be consulted for output.
    use_cached_output = True

    def __init__(self, request, edit_mode=None):
        if edit_mode is None:
            edit_mode = markers.is_edit_mode(request)

        self.request = request
        self.edit_mode = edit_mode
        optimize_logger_level(logger, logging.DEBUG)

    def render_items(self, placeholder, items, parent_object=None, template_name=None, cachable=None):
        """
        The main rendering sequence.
        """
        # Unless it was done before, disable polymorphic effects.
        is_queryset = False
        if hasattr(items, "non_polymorphic"):
            is_queryset = True
            if not items.polymorphic_disabled and items._result_cache is None:
                items = items.non_polymorphic()

        # See if the queryset contained anything.
        # This test is moved here, to prevent earlier query execution.
        if not items:
            logger.debug("- no items in placeholder '%s'", get_placeholder_debug_name(placeholder))
            return ContentItemOutput(mark_safe(u"<!-- no items in placeholder '{0}' -->".format(escape(get_placeholder_name(placeholder)))), cacheable=True)

        # Tracked data during rendering:
        result = self.result_class(
            request=self.request,
            parent_object=parent_object,
            placeholder=placeholder,
            items=items,
            all_cacheable=self._can_cache_merged_output(template_name, cachable),
        )
        if self.edit_mode:
            result.set_uncachable()

        if is_queryset:
            # Phase 1: get cached output
            self._fetch_cached_output(items, result=result)
            result.fetch_remaining_instances(queryset=items)
        else:
            # The items is either a list of manually created items, or it's a QuerySet.
            # Can't prevent reading the subclasses only, so don't bother with caching here.
            result.add_remaining_list(items)

        # Start the actual rendering of remaining items.
        if result.remaining_items:
            # Phase 2: render remaining items
            self._render_uncached_items(result.remaining_items, result=result)

        # And merge all items together.
        return self.merge_output(result, items, template_name)

    def _fetch_cached_output(self, items, result):
        """
        First try to fetch all items from the cache.
        The items are 'non-polymorphic', so only point to their base class.
        If these are found, there is no need to query the derived data from the database.
        """
        if not appsettings.FLUENT_CONTENTS_CACHE_OUTPUT or not self.use_cached_output:
            result.add_remaining_list(items)
            return

        for contentitem in items:
            result.add_ordering(contentitem)
            output = None

            try:
                plugin = contentitem.plugin
            except PluginNotFound as ex:
                result.store_exception(contentitem, ex)  # Will deal with that later.
                logger.debug("- item #%s has no matching plugin: %s", contentitem.pk, str(ex))
                continue

            # Respect the cache output setting of the plugin
            if self.can_use_cached_output(contentitem):
                result.add_plugin_timeout(plugin)
                output = plugin.get_cached_output(result.placeholder_name, contentitem)

                # Support transition to new output format.
                if output is not None and not isinstance(output, ContentItemOutput):
                    output = None
                    logger.debug("Flushed cached output of {0}#{1} to store new ContentItemOutput format (key: {2})".format(
                        plugin.type_name,
                        contentitem.pk,
                        get_placeholder_name(contentitem.placeholder)
                    ))

            # For debugging, ignore cached values when the template is updated.
            if output and settings.DEBUG:
                cachekey = get_rendering_cache_key(result.placeholder_name, contentitem)
                if is_template_updated(self.request, contentitem, cachekey):
                    output = None

            if output:
                result.store_output(contentitem, output)
            else:
                result.add_remaining(contentitem)

    def can_use_cached_output(self, contentitem):
        """
        Tell whether the code should try reading cached output
        """
        plugin = contentitem.plugin
        return appsettings.FLUENT_CONTENTS_CACHE_OUTPUT and plugin.cache_output and contentitem.pk

    def _render_uncached_items(self, items, result):
        """
        Render a list of items, that didn't exist in the cache yet.
        """
        for contentitem in items:
            # Render the item.
            # Allow derived classes to skip it.
            try:
                output = self.render_item(contentitem)
            except PluginNotFound as ex:
                result.store_exception(contentitem, ex)
                logger.debug("- item #%s has no matching plugin: %s", contentitem.pk, str(ex))
                continue
            except SkipItem:
                result.set_skipped(contentitem)
                continue

            # Try caching it.
            self._try_cache_output(contentitem, output, result=result)
            if self.edit_mode:
                output.html = markers.wrap_contentitem_output(output.html, contentitem)

            result.store_output(contentitem, output)

    def render_item(self, contentitem):
        """
        Render the individual item.
        May raise :class:`SkipItem` to ignore an item.
        """
        render_language = get_render_language(contentitem)
        with smart_override(render_language):
            # Plugin output is likely HTML, but it should be placed in mark_safe() to raise awareness about escaping.
            # This is just like Django's Input.render() and unlike Node.render().
            return contentitem.plugin._render_contentitem(self.request, contentitem)

    def _try_cache_output(self, contentitem, output, result):
        plugin = contentitem.plugin
        if self._can_cache_output(plugin, output) and contentitem.pk:
            # Cache the output
            plugin.set_cached_output(result.placeholder_name, contentitem, output)

            if plugin.cache_output_per_site:
                # Unsupported: can't cache global output for placeholder yet if output differs per SITE_ID
                # Placeholders only have a single entry, the SITE_ID is not part of it's cache key yet.
                logger.debug("- item #%s is blocks full placeholder caching. Prevented by %r.cache_output_per_site", contentitem.pk, contentitem.plugin)
                result.set_uncachable()
        else:
            # An item blocks caching the complete placeholder.
            result.set_uncachable()
            if appsettings.FLUENT_CONTENTS_CACHE_OUTPUT:
                logger.debug("- item #%s is NOT cachable! Prevented by %r", contentitem.pk, contentitem.plugin)

    def _can_cache_output(self, plugin, output):
         return appsettings.FLUENT_CONTENTS_CACHE_OUTPUT \
                and plugin.cache_output \
                and output.cacheable

    def _can_cache_merged_output(self, template_name, cachable=None):
        """
        Determine whether merged results using a template could be cached.

        Note caching won't happen by default when merging via a template,
        because there is no way to tell whether that can be expired/invalidated.
        The caller should explicitly state that the template is cachable.
        """
        if cachable is None:
            # None = choose. by default True unless there is a template.
            return not bool(template_name)
        else:
            # Just return what the calling code already specified.
            return cachable

    def merge_output(self, result, items, template_name):
        """
        Combine all rendered items. Allow rendering the items with a template,
        to inserting separators or nice start/end code.
        """
        html_output, media = self.get_html_output(result, items)

        if not template_name:
            merged_html = mark_safe(u''.join(html_output))
        else:
            context = {
                'contentitems': list(zip(items, html_output)),
                'parent_object': result.parent_object,  # Can be None
                'edit_mode': self.edit_mode,
            }
            merged_html = render_to_string(template_name, context, context_instance=RequestContext(self.request))

        return ContentItemOutput(merged_html, media, cacheable=result.all_cacheable, cache_timeout=result.all_timeout)

    def get_html_output(self, result, items):
        """
        Collect all HTML from the rendered items, in the correct ordering.
        The media is also collected in the same ordering, in case it's handled by django-compressor for example.
        """
        html_output = []
        merged_media = Media()
        for contentitem, output in result.get_output(include_exceptions=True):
            if output is ResultTracker.MISSING:
                # Likely get_real_instances() didn't return an item for it.
                # The get_real_instances() didn't return an item for the derived table. This happens when either:
                # 1. that table is truncated/reset, while there is still an entry in the base ContentItem table.
                #    A query at the derived table happens every time the page is being rendered.
                # 2. the model was completely removed which means there is also a stale ContentType object.
                class_name = _get_stale_item_class_name(contentitem)
                html_output.append(mark_safe(u"<!-- Missing derived model for ContentItem #{id}: {cls}. -->\n".format(id=contentitem.pk, cls=class_name)))
                logger.warning("Missing derived model for ContentItem #{id}: {cls}.".format(id=contentitem.pk, cls=class_name))
            elif isinstance(output, Exception):
                html_output.append(u'<!-- error: {0} -->\n'.format(str(output)))
            else:
                html_output.append(output.html)
                add_media(merged_media, output.media)

        return html_output, merged_media


class PlaceholderRenderingPipe(RenderingPipe):
    """
    The rendering of placeholders.
    """

    def render_placeholder(self, placeholder, parent_object=None, template_name=None, cachable=None, limit_parent_language=True, fallback_language=None):
        """
        The main rendering sequence for placeholders.
        This will do all the magic for caching, and call :func:`render_items` in the end.
        """
        placeholder_name = get_placeholder_debug_name(placeholder)
        logger.debug("Rendering placeholder '%s'", placeholder_name)

        # Determine whether the placeholder can be cached.
        cachable = self._can_cache_merged_output(template_name, cachable)
        try_cache = cachable and self.may_cache_placeholders()
        logger.debug("- try_cache=%s cachable=%s template_name=%s", try_cache, cachable, template_name)

        if parent_object is None:
            # To support filtering the placeholders by parent language, the parent object needs to be known.
            # Fortunately, the PlaceholderFieldDescriptor makes sure this doesn't require an additional query.
            parent_object = placeholder.parent

        # Fetch the placeholder output from cache.
        language_code = get_parent_language_code(parent_object)
        cache_key = None
        output = None
        if try_cache:
            cache_key = get_placeholder_cache_key_for_parent(parent_object, placeholder.slot, language_code)
            output = cache.get(cache_key)
            if output:
                logger.debug("- fetched cached output")

        if output is None:
            # Get the items, and render them
            items, is_fallback = self._get_placeholder_items(placeholder, parent_object, limit_parent_language, fallback_language, try_cache)
            output = self.render_items(placeholder, items, parent_object, template_name, cachable)

            if is_fallback:
                # Caching fallbacks is not supported yet,
                # content could be rendered in a different gettext language domain.
                output.cacheable = False

            # Store the full-placeholder contents in the cache.
            if try_cache and output.cacheable:
                if output.cache_timeout is not DEFAULT_TIMEOUT:
                    # The timeout is based on the minimal timeout used in plugins.
                    cache.set(cache_key, output, output.cache_timeout)
                else:
                    # Don't want to mix into the default 0/None issue.
                    cache.set(cache_key, output)

        return output

    def _get_placeholder_items(self, placeholder, parent_object, limit_parent_language, fallback_language, try_cache):
        # No full-placeholder cache. Get the items
        items = placeholder.get_content_items(parent_object, limit_parent_language=limit_parent_language).non_polymorphic()
        if is_queryset_empty(items):  # Detect qs.none() was applied
            logging.debug("- skipping regular language, parent object has no translation for it.")

        if fallback_language \
        and not items:  # NOTES: performs query, so hence the .non_polymorphic() above
            # There are no items, but there is a fallback option. Try it.
            language_code = appsettings.FLUENT_CONTENTS_DEFAULT_LANGUAGE_CODE if fallback_language is True else fallback_language
            logger.debug("- reading fallback language %s, try_cache=%s", language_code, try_cache)
            items = placeholder.get_content_items(parent_object, limit_parent_language=False).translated(language_code).non_polymorphic()
            return items, True
        else:
            return items, False

    @classmethod
    def may_cache_placeholders(cls):
        return appsettings.FLUENT_CONTENTS_CACHE_OUTPUT \
           and appsettings.FLUENT_CONTENTS_CACHE_PLACEHOLDER_OUTPUT


class SkipItem(RuntimeError):
    pass


def _get_stale_item_class_name(item):
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
