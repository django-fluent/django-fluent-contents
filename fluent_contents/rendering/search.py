import django
from django.utils.safestring import mark_safe
from fluent_contents.models import ContentItemOutput
from fluent_contents.utils.search import get_cleaned_string
from .core import PlaceholderRenderingPipe, SkipItem, ResultTracker
from .utils import get_dummy_request

if django.VERSION >= (1, 8):
    # Use modern lru_cache, avoids deprecation warnings. Needs Python 2.7+
    from django.utils.lru_cache import lru_cache
    _get_dummy_search_request = lru_cache()(get_dummy_request)
else:
    from django.utils.functional import memoize
    _SEARCH_REQUEST_CACHE = {}
    _get_dummy_search_request = memoize(get_dummy_request, _SEARCH_REQUEST_CACHE, 1)


class SearchResultTracker(ResultTracker):

    def store_output(self, contentitem, output):
        # Strip all output from HTML tags while collecting
        # (the output is already cached at this point)
        output.html = get_cleaned_string(output.html)
        output.cacheable = False
        super(SearchResultTracker, self).store_output(contentitem, output)


class SearchRenderingPipe(PlaceholderRenderingPipe):
    """
    Variation of the rendering, suitable for search indexers.
    """
    result_class = SearchResultTracker

    def __init__(self, language):
        request = get_dummy_request(language)
        super(SearchRenderingPipe, self).__init__(request)

    def can_use_cached_output(self, contentitem):
        """
        Read the cached output - only when search needs it.
        """
        return contentitem.plugin.search_output and not contentitem.plugin.search_fields \
           and super(SearchRenderingPipe, self).can_use_cached_output(contentitem)

    def render_item(self, contentitem):
        """
        Render the item - but render as search text instead.
        """
        plugin = contentitem.plugin
        if not plugin.search_output and not plugin.search_fields:
            # Only render items when the item was output will be indexed.
            raise SkipItem

        if not plugin.search_output:
            output = ContentItemOutput('', cacheable=False)
        else:
            output = super(SearchRenderingPipe, self).render_item(contentitem)

        if plugin.search_fields:
            # Just add the results into the output, but avoid caching that somewhere.
            output.html += plugin.get_search_text(contentitem)
            output.cacheable = False

        return output

    def _try_cache_output(self, contentitem, output, result):
        # Don't cache renderings for a search index run yet.
        # This might be really broken - just a safety measure which can likely be removed.
        return

    def merge_output(self, result, items, template_name):
        # Collect all individual rendered items.
        html_output = []
        for contentitem, output in result.get_output():
            html_output.append(output.html)

        merged_html = mark_safe(u''.join(html_output))
        return ContentItemOutput(merged_html, cacheable=False)   # since media is not included, don't cache this
