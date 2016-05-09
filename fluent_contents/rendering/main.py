"""
The main API for rendering content.
This is exposed via __init__.py
"""
from django.core.cache import cache
from django.utils.safestring import mark_safe
from fluent_contents.cache import get_placeholder_cache_key_for_parent
from fluent_contents.models import ContentItemOutput, get_parent_language_code
from .core import RenderingPipe, PlaceholderRenderingPipe
from .search import SearchRenderingPipe
from . import markers


def get_cached_placeholder_output(parent_object, placeholder_name):
    """
    Return cached output for a placeholder, if available.
    This avoids fetching the Placeholder object.
    """
    if not PlaceholderRenderingPipe.may_cache_placeholders():
        return None

    language_code = get_parent_language_code(parent_object)
    cache_key = get_placeholder_cache_key_for_parent(parent_object, placeholder_name, language_code)
    return cache.get(cache_key)


def render_placeholder(request, placeholder, parent_object=None, template_name=None, cachable=None, limit_parent_language=True, fallback_language=None):
    """
    Render a :class:`~fluent_contents.models.Placeholder` object.
    Returns a :class:`~fluent_contents.models.ContentItemOutput` object
    which contains the HTML output and :class:`~django.forms.Media` object.

    This function also caches the complete output of the placeholder
    when all individual items are cacheable.

    :param request: The current request object.
    :type request: :class:`~django.http.HttpRequest`
    :param placeholder: The placeholder object.
    :type placeholder: :class:`~fluent_contents.models.Placeholder`
    :param parent_object: Optional, the parent object of the placeholder (already implied by the placeholder)
    :param template_name: Optional template name used to concatenate the placeholder output.
    :type template_name: str | None
    :param cachable: Whether the output is cachable, otherwise the full output will not be cached.
                     Default: False when using a template, True otherwise.
    :type cachable: bool | None
    :param limit_parent_language: Whether the items should be limited to the parent language.
    :type limit_parent_language: bool
    :param fallback_language: The fallback language to use if there are no items in the current language. Passing ``True`` uses the default :ref:`FLUENT_CONTENTS_DEFAULT_LANGUAGE_CODE`.
    :type fallback_language: bool/str
    :rtype: :class:`~fluent_contents.models.ContentItemOutput`
    """
    output = PlaceholderRenderingPipe(request).render_placeholder(
        placeholder=placeholder,
        parent_object=parent_object,
        template_name=template_name,
        cachable=cachable,
        limit_parent_language=limit_parent_language,
        fallback_language=fallback_language
    )

    # Wrap the result after it's stored in the cache.
    if markers.is_edit_mode(request):
        output.html = markers.wrap_placeholder_output(output.html, placeholder)

    return output


def render_content_items(request, items, template_name=None, cachable=None):
    """
    Render a list of :class:`~fluent_contents.models.ContentItem` objects as HTML string.
    This is a variation of the :func:`render_placeholder` function.

    Note that the items are not filtered in any way by parent or language.
    The items are rendered as-is.

    :param request: The current request object.
    :type request: :class:`~django.http.HttpRequest`
    :param items: The list or queryset of objects to render. Passing a queryset is preferred.
    :type items: list or queryset of :class:`~fluent_contents.models.ContentItem`.
    :param template_name: Optional template name used to concatenate the placeholder output.
    :type template_name: Optional[str]
    :param cachable: Whether the output is cachable, otherwise the full output will not be cached.
                     Default: False when using a template, True otherwise.
    :type cachable: Optional[bool]

    :rtype: :class:`~fluent_contents.models.ContentItemOutput`
    """
    if not items:
        output = ContentItemOutput(mark_safe(u"<!-- no items to render -->"))
    else:
        output = RenderingPipe(request).render_items(
            placeholder=None,
            items=items,
            parent_object=None,
            template_name=template_name,
            cachable=cachable
        )

    # Wrap the result after it's stored in the cache.
    if markers.is_edit_mode(request):
        output.html = markers.wrap_anonymous_output(output.html)

    return output


def render_placeholder_search_text(placeholder, fallback_language=None):
    """
    Render a :class:`~fluent_contents.models.Placeholder` object to search text.
    This text can be used by an indexer (e.g. haystack) to produce content search for a parent object.

    :param placeholder: The placeholder object.
    :type placeholder: :class:`~fluent_contents.models.Placeholder`
    :param fallback_language: The fallback language to use if there are no items in the current language.
                              Passing ``True`` uses the default :ref:`FLUENT_CONTENTS_DEFAULT_LANGUAGE_CODE`.
    :type fallback_language: bool|str
    :rtype: str
    """
    parent_object = placeholder.parent   # this is a cached lookup thanks to PlaceholderFieldDescriptor
    language = get_parent_language_code(parent_object)
    output = SearchRenderingPipe(language).render_placeholder(
        placeholder=placeholder,
        parent_object=parent_object,
        fallback_language=fallback_language
    )
    return output.html   # Tags already stripped.
