from django.utils.safestring import mark_safe

from fluent_contents.models import ContentItemOutput
from fluent_contents.utils.search import get_cleaned_string

from .core import PlaceholderRenderingPipe, ResultTracker, SkipItem
from .utils import get_dummy_request


class SearchResultTracker(ResultTracker):
    def store_output(self, contentitem, output):
        # Strip all output from HTML tags while collecting
        # (the output is already cached at this point)
        output.html = get_cleaned_string(output.html)
        output.cacheable = False
        super().store_output(contentitem, output)


class SearchRenderingPipe(PlaceholderRenderingPipe):
    """
    Variation of the rendering, suitable for search indexers.
    """

    result_class = SearchResultTracker

    def __init__(self, language):
        request = get_dummy_request(language)
        super().__init__(request)

    def can_use_cached_output(self, contentitem):
        """
        Read the cached output - only when search needs it.
        """
        return (
            contentitem.plugin.search_output
            and not contentitem.plugin.search_fields
            and super().can_use_cached_output(contentitem)
        )

    def render_item(self, contentitem):
        """
        Render the item - but render as search text instead.
        """
        plugin = contentitem.plugin
        if not plugin.search_output and not plugin.search_fields:
            # Only render items when the item was output will be indexed.
            raise SkipItem

        if not plugin.search_output:
            output = ContentItemOutput("", cacheable=False)
        else:
            output = super().render_item(contentitem)

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

        # since media is not included, cachable is false
        merged_html = mark_safe("".join(html_output))
        return ContentItemOutput(merged_html, cacheable=False)
