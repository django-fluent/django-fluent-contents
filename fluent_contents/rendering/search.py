from django.utils.functional import memoize
from django.utils.safestring import mark_safe
from fluent_contents.models import ContentItemOutput
from fluent_contents.utils.search import get_cleaned_string
from .core import PlaceholderRenderingPipe, SkipItem, ResultTracker
from .utils import get_dummy_request


_SEARCH_REQUEST_CACHE = {}
_get_dummy_search_request = memoize(get_dummy_request, _SEARCH_REQUEST_CACHE, 1)


class SearchResultTracker(ResultTracker):
    def add_output(self, contentitem, output):
        # Strip all output from HTML tags while collecting
        # (the output is already cached at this point)
        output.html = get_cleaned_string(output.html)
        output.cacheable = False
        super(SearchResultTracker, self).add_output(contentitem, output)


class SearchRenderingPipe(PlaceholderRenderingPipe):
    """
    Variation of the rendering, suitable for search indexers.
    """
    result_class = SearchResultTracker

    def __init__(self, language):
        request = get_dummy_request(language)
        super(SearchRenderingPipe, self).__init__(request)

    def should_fetch_cached_output(self, contentitem):
        # Only fetch items from the cache when the item was output indexed.
        return contentitem.plugin.search_output and not contentitem.plugin.search_fields \
           and super(SearchRenderingPipe, self).should_fetch_cached_output(contentitem)

    def render_item(self, contentitem):
        plugin = contentitem.plugin
        if not plugin.search_output and not plugin.search_fields:
            # Only render items when the item was output will be indexed.
            raise SkipItem

        if plugin.search_output:
            output = super(SearchRenderingPipe, self).render_item(contentitem)
        else:
            output = ContentItemOutput('')

        if plugin.search_fields:
            output.html += self.get_search_fields(contentitem)
            output.cacheable = False

        return output

    def _try_cache_output(self, contentitem, output, result):
        # Don't cache renderings for a search index run yet.
        # This might be really broken - just a safety measure which can likely be removed.
        return

    def merge_output(self, result, items, template_name):
        # Collect all individual rendered items.
        html_output = []
        for item_id, output in result.get_output():
            html_output.append(output.html)

        merged_html = mark_safe(u''.join(html_output))
        return ContentItemOutput(merged_html, cacheable=False)   # since media is not included, don't cache this

    def get_search_fields(self, contentitem):
        """
        Extract the search fields from the model, add these to the index.
        """
        plugin = contentitem.plugin
        values = []
        for field_name in plugin.search_fields:
            value = getattr(contentitem, field_name)

            # Just assume all strings may contain HTML.
            # Not checking for just the PluginHtmlField here.
            if value and isinstance(value, six.string_types):
                value = strip_tags(force_unicode(value))

            values.append(value)

        return _clean_join(u" ", values)



def _get_cleaned_bits(data):
    """
    Cleanup a string/HTML output to consist of words only.
    """
    stripped = strip_tags(force_unicode(data))
    return smart_split(stripped)


def _clean_join(separator, iterable):
    """
    Filters out iterable to only join non empty items.
    """
    return separator.join(filter(None, iterable))
