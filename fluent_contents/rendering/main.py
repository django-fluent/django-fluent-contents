"""
The main API for rendering content.
This is exposed via __init__.py
"""
import logging
from django.core.cache import cache
from django.utils.safestring import mark_safe
from fluent_utils.django_compat import is_queryset_empty
from fluent_contents.rendering.core import RenderingPipe
from fluent_contents import appsettings
from fluent_contents.cache import get_placeholder_cache_key_for_parent
from fluent_contents.models import ContentItemOutput, get_parent_language_code, DEFAULT_TIMEOUT
from . import markers
from .utils import get_placeholder_debug_name, optimize_logger_level

logger = logging.getLogger('fluent_contents.rendering')


def get_cached_placeholder_output(parent_object, placeholder_name):
    """
    Return cached output for a placeholder, if available.
    This avoids fetching the Placeholder object.
    """
    if not appsettings.FLUENT_CONTENTS_CACHE_OUTPUT \
    or not appsettings.FLUENT_CONTENTS_CACHE_PLACEHOLDER_OUTPUT:
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
    optimize_logger_level(logger, logging.DEBUG)
    placeholder_name = get_placeholder_debug_name(placeholder)
    logger.debug("Rendering placeholder '%s'", placeholder_name)

    if cachable is None:
        # default: True unless there is a template.
        cachable = not bool(template_name)

    # Caching will not happen when rendering via a template,
    # because there is no way to tell whether that can be expired/invalidated.
    try_cache = appsettings.FLUENT_CONTENTS_CACHE_OUTPUT \
            and appsettings.FLUENT_CONTENTS_CACHE_PLACEHOLDER_OUTPUT \
            and cachable
    cache_key = None
    output = None

    logger.debug("- try_cache=%s cachable=%s template_name=%s", try_cache, cachable, template_name)

    if parent_object is None:
        # To support filtering the placeholders by parent language, the parent object needs to be known.
        # Fortunately, the PlaceholderFieldDescriptor makes sure this doesn't require an additional query.
        parent_object = placeholder.parent

    language_code = get_parent_language_code(parent_object)
    if try_cache:
        cache_key = get_placeholder_cache_key_for_parent(parent_object, placeholder.slot, language_code)
        output = cache.get(cache_key)

    if output is None:
        # No full-placeholder cache. Get the items
        items = placeholder.get_content_items(parent_object, limit_parent_language=limit_parent_language).non_polymorphic()
        if is_queryset_empty(items):  # Detect qs.none() was applied
            logging.debug("- skipping regular language, parent object has no translation for it.")

        if fallback_language \
        and not items:  # NOTES: performs query, so hence the .non_polymorphic() above
            # There are no items, but there is a fallback option.
            # This is not supported yet, content can be rendered in a different gettext language domain.
            try_cache = False

            language_code = appsettings.FLUENT_CONTENTS_DEFAULT_LANGUAGE_CODE if fallback_language is True else fallback_language
            logger.debug("- reading fallback language %s, try_cache=%s", language_code, try_cache)
            items = placeholder.get_content_items(parent_object, limit_parent_language=False).translated(language_code).non_polymorphic()

        # Perform the rendering
        output = RenderingPipe(request).render_items(placeholder, items, parent_object=parent_object, template_name=template_name, cachable=cachable)

        # Store the full-placeholder contents in the cache.
        if try_cache and output.cacheable and cache_key is not None:
            # The timeout takes notice of the minimal timeout used in plugins.
            if output.cache_timeout is not DEFAULT_TIMEOUT:
                cache.set(cache_key, output, output.cache_timeout)
            else:
                # Don't want to mix into the default 0/None issue.
                cache.set(cache_key, output)
    else:
        logger.debug("- fetched cached output")

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
    :type template_name: str
    :param cachable: Whether the output is cachable, otherwise the full output will not be cached.
                     Default: False when using a template, True otherwise.
    :type cachable: bool | None

    :rtype: :class:`~fluent_contents.models.ContentItemOutput`
    """
    if not items:
        output = ContentItemOutput(mark_safe(u"<!-- no items to render -->"))
    else:
        output = RenderingPipe(request).render_items(None, items, parent_object=None, template_name=template_name, cachable=cachable)

    # Wrap the result after it's stored in the cache.
    if markers.is_edit_mode(request):
        output.html = markers.wrap_anonymous_output(output.html)

    return output
