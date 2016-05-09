"""
This module provides functions to render placeholder content manually.

The functions are available outside the regular templatetags,
so it can be called outside the templates as well.

Contents is cached in memcache whenever possible, only the remaining items are queried.
The templatetags also use these functions to render the :class:`~fluent_contents.models.ContentItem` objects.
"""
from .main import render_placeholder, render_content_items, get_cached_placeholder_output, render_placeholder_search_text
from .markers import is_edit_mode, set_edit_mode
from .media import register_frontend_media, get_frontend_media


__all__ = (
    # Main
    'get_cached_placeholder_output',
    'render_placeholder',
    'render_content_items',
    'render_placeholder_search_text',

    # Media
    'get_frontend_media',
    'register_frontend_media',

    # Markers
    'is_edit_mode',
    'set_edit_mode',
)
