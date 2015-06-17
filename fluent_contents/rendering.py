"""
This module provides functions to render placeholder content manually.
Contents is cached in memcache whenever possible, only the remaining items are queried.
The templatetags also use these functions to render the :class:`~fluent_contents.models.ContentItem` objects.
"""
import django
import logging, os, six
from future.builtins import str
from django.conf import settings
from django.core.cache import cache
from django.forms import Media
from django.template.context import RequestContext
from django.template.loader import render_to_string, select_template
from django.utils.html import conditional_escape, escape
from django.utils.safestring import mark_safe
from django.utils.translation import get_language
from parler.utils.context import smart_override
from fluent_utils.django_compat import is_queryset_empty
from fluent_contents import appsettings
from fluent_contents.cache import get_rendering_cache_key, get_placeholder_cache_key_for_parent
from fluent_contents.extensions import PluginNotFound, ContentPlugin
from fluent_contents.models import ContentItemOutput, ImmutableMedia, get_parent_language_code, DEFAULT_TIMEOUT

try:
    from django.template.backends.django import Template as TemplateAdapter
except ImportError:
    TemplateAdapter = None

# This code is separate from the templatetags,
# so it can be called outside the templates as well.


logger = logging.getLogger(__name__)
_LOG_DEBUG = None

def _optimize_logger():
    # At runtime, when logging is not active,
    # replace the .debug() call with a no-op.
    global _LOG_DEBUG
    if _LOG_DEBUG is None:
        _LOG_DEBUG = logger.isEnabledFor(logging.DEBUG)
        if not _LOG_DEBUG:
            def dummy_debug(msg, *args, **kwargs):
                pass
            logger.debug = dummy_debug


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
    _optimize_logger()
    placeholder_name = _get_placeholder_name(placeholder)
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
        if _LOG_DEBUG and is_queryset_empty(items):  # Detect qs.none() was applied
            logging.debug("- skipping regular language, parent object has no translation for it.")

        if fallback_language \
        and not items:  # NOTES: performs query, so hence the .non_polymorphic() above
            # There are no items, but there is a fallback option.
            # This is not supported yet, content can be rendered in a different gettext language domain.
            try_cache = False

            language_code = appsettings.FLUENT_CONTENTS_DEFAULT_LANGUAGE_CODE if fallback_language is True else fallback_language
            logger.debug("- reading fallback language %s, try_cache=%s", language_code, try_cache)
            items = placeholder.get_content_items(parent_object, limit_parent_language=False).translated(language_code).non_polymorphic()

        output = _render_items(request, placeholder, items, parent_object=parent_object, template_name=template_name, cachable=cachable)

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

    if is_edit_mode(request):
        output.html = _wrap_placeholder_output(output.html, placeholder)

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
        output = _render_items(request, None, items, parent_object=None, template_name=template_name, cachable=cachable)

    if is_edit_mode(request):
        output.html = _wrap_anonymous_output(output.html)

    return output


def set_edit_mode(request, state):
    """
    Enable the edit mode; placeholders and plugins will be wrapped in a ``<div>`` that exposes metadata for frontend editing.
    """
    setattr(request, '_fluent_contents_edit_mode', bool(state))


def is_edit_mode(request):
    """
    Return whether edit mode is enabled; output is wrapped in ``<div>`` elements with metadata for frontend editing.
    """
    return getattr(request, '_fluent_contents_edit_mode', False)


def register_frontend_media(request, media):
    """
    Add a :class:`~django.forms.Media` class to the current request.
    This will be rendered by the ``render_plugin_media`` template tag.
    """
    if not hasattr(request, '_fluent_contents_frontend_media'):
        request._fluent_contents_frontend_media = Media()

    _add_media(request._fluent_contents_frontend_media, media)


def get_frontend_media(request):
    """
    Return the media that was registered in the request object.
    """
    return getattr(request, '_fluent_contents_frontend_media', None) or ImmutableMedia.empty_instance


def _render_items(request, placeholder, items, parent_object=None, template_name=None, cachable=False):
    edit_mode = is_edit_mode(request)
    item_output = {}
    output_ordering = []
    all_cacheable = True
    all_timeout = DEFAULT_TIMEOUT

    placeholder_cache_name = '@global@' if placeholder is None else placeholder.slot

    if not hasattr(items, "non_polymorphic"):
        # The items is either a list of manually created items, or it's a QuerySet.
        # Can't prevent reading the subclasses only, so don't bother with caching here.
        remaining_items = items
        output_ordering = [item.pk or id(item) for item in items]
    else:
        # Unless it was done before, disable polymorphic effects.
        if not items.polymorphic_disabled:
            items = items.non_polymorphic()

        # First try to fetch all items non-polymorphic from memcache
        # If these are found, there is no need to query the derived data from the database.
        remaining_items = []
        for i, contentitem in enumerate(items):
            output_ordering.append(contentitem.pk)
            output = None
            # Respect the cache output setting of the plugin
            if appsettings.FLUENT_CONTENTS_CACHE_OUTPUT:
                try:
                    plugin = contentitem.plugin
                except PluginNotFound:
                    pass
                else:
                    if plugin.cache_output and contentitem.pk:
                        output = plugin.get_cached_output(placeholder_cache_name, contentitem)
                        all_timeout = _min_timeout(all_timeout, plugin.cache_timeout)

                        # Support transition to new output format.
                        if output is not None and not isinstance(output, ContentItemOutput):
                            output = None
                            logger.debug("Flushed cached output of {0}#{1} to store new ContentItemOutput format (key: {2})".format(plugin.type_name, contentitem.pk, placeholder_cache_name))

            # For debugging, ignore cached values when the template is updated.
            if output and settings.DEBUG:
                cachekey = get_rendering_cache_key(placeholder_cache_name, contentitem)
                if _is_template_updated(request, contentitem, cachekey):
                    output = None

            if output:
                item_output[contentitem.pk] = output
            else:
                remaining_items.append(contentitem)

        # Fetch derived table data for all objects not found in memcached
        if remaining_items:
            remaining_items = items.get_real_instances(remaining_items)

    # See if the queryset contained anything.
    # This test is moved here, to prevent earlier query execution.
    if not items:
        placeholder_name = _get_placeholder_name(placeholder)
        logger.debug("- no items in placeholder '%s'", placeholder_name)
        return ContentItemOutput(mark_safe(u"<!-- no items in placeholder '{0}' -->".format(escape(placeholder_name))))
    elif remaining_items:
        # Render remaining items
        for contentitem in remaining_items:
            try:
                plugin = contentitem.plugin
            except PluginNotFound as e:
                output = ContentItemOutput(mark_safe(u'<!-- error: {0} -->\n'.format(str(e))))
                logger.debug("- item #%s has no matching plugin: %s", contentitem.pk, str(e))
            else:
                if plugin.render_ignore_item_language \
                or (plugin.cache_output and plugin.cache_output_per_language):
                    # Render the template in the current language.
                    # The cache also stores the output under the current language code.
                    #
                    # It would make sense to apply this for fallback content too,
                    # but that would be ambiguous however because the parent_object could also be a fallback,
                    # and that case can't be detected here. Hence, better be explicit when desiring multi-lingual content.
                    render_language = get_language()  # Avoid switching the content,
                else:
                    # Render the template in the ContentItem language.
                    # This makes sure that {% trans %} tag output matches the language of the model field data.
                    render_language = contentitem.language_code

                with smart_override(render_language):
                    # Plugin output is likely HTML, but it should be placed in mark_safe() to raise awareness about escaping.
                    # This is just like Django's Input.render() and unlike Node.render().
                    output = plugin._render_contentitem(request, contentitem)

                if appsettings.FLUENT_CONTENTS_CACHE_OUTPUT \
                and plugin.cache_output \
                and output.cacheable \
                and contentitem.pk:
                    # Cache the output
                    contentitem.plugin.set_cached_output(placeholder_cache_name, contentitem, output)
                else:
                    # Item blocks caching the complete placeholder.
                    all_cacheable = False

                    if appsettings.FLUENT_CONTENTS_CACHE_OUTPUT:
                        logger.debug("- item #%s is NOT cachable! Prevented by %r", contentitem.pk, plugin)

                if edit_mode:
                    output.html = _wrap_contentitem_output(output.html, contentitem)

            item_id = contentitem.pk or id(contentitem)
            item_output[item_id] = output

    # Order all rendered items in the correct sequence.  The derived tables could be truncated/reset,
    # so the base class model indexes don't necessary match with the derived indexes. Hence the dict + KeyError handling.
    #
    # The media is also collected in the same ordering, in case it's handled by django-compressor for example.
    output_ordered = []
    merged_media = Media()
    for pk in output_ordering:
        try:
            output = item_output[pk]
            output_ordered.append(output.html)
            _add_media(merged_media, output.media)
        except KeyError:
            # The get_real_instances() didn't return an item for the derived table. This happens when either:
            # - that table is truncated/reset, while there is still an entry in the base ContentItem table.
            #   A query at the derived table happens every time the page is being rendered.
            # - the model was completely removed which means there is also a stale ContentType object.
            item = next(item for item in items if item.pk == pk)
            try:
                class_name = item.plugin.type_name
            except PluginNotFound:
                # Derived table isn't there because the model has been removed.
                # There is a stale ContentType object, no plugin associated or loaded.
                class_name = 'content type is stale'

            output_ordered.append(u"<!-- Missing derived model for ContentItem #{id}: {cls}. -->\n".format(id=pk, cls=class_name))
            logger.warning("Missing derived model for ContentItem #{id}: {cls}.".format(id=pk, cls=class_name))
            pass


    # Combine all rendered items. Allow rendering the items with a template,
    # to inserting separators or nice start/end code.
    if not template_name:
        merged_output = mark_safe(''.join(output_ordered))
    else:
        context = {
            'contentitems': list(zip(items, output_ordered)),
            'parent_object': parent_object,  # Can be None
            'edit_mode': edit_mode,
        }
        merged_output = render_to_string(template_name, context, context_instance=RequestContext(request))

        # By default, cachable is False for templates.
        # Template name is ambiguous, can't reliable expire.
        # Nor can be determined whether the template is consistent or not cacheable.

    if not cachable:
        all_cacheable = False

    return ContentItemOutput(merged_output, merged_media, cacheable=all_cacheable, cache_timeout=all_timeout)


def _wrap_placeholder_output(html, placeholder):
    return mark_safe('<div class="cp-editable-placeholder" id="cp-editable-placeholder-{slot}" data-placeholder-id="{id}" data-placeholder-slot="{slot}">' \
           '{html}' \
           '</div>\n'.format(
        html=conditional_escape(html),
        id=placeholder.id,
        slot=placeholder.slot,
    ))


def _wrap_anonymous_output(html):
    return mark_safe('<div class="cp-editable-placeholder">' \
           '{html}' \
           '</div>\n'.format(
        html=conditional_escape(html),
    ))


def _wrap_contentitem_output(html, contentitem):
    return mark_safe('<div class="cp-editable-contentitem" data-itemtype="{itemtype}" data-item-id="{id}">' \
           '{html}' \
           '</div>\n'.format(
        html=conditional_escape(html),
        itemtype=contentitem.__class__.__name__,  # Same as ContentPlugin.type_name
        id=contentitem.id,
    ))


def _get_placeholder_name(placeholder):
    # TODO: Cheating here with knowledge of "fluent_contents.plugins.sharedcontent" package:
    #       prevent unclear message in <!-- no items in '..' placeholder --> debug output.
    if placeholder.slot == 'shared_content':
        sharedcontent = placeholder.parent
        return "shared_content:{0}".format(sharedcontent.slug)

    return placeholder.slot


def _min_timeout(val1, val2):
    # Avoid min(int, object). That may work but it's
    # a CPython implementation detail to compare that as "int" < "object"
    if not isinstance(val2, six.integer_types):
        return val1

    if not isinstance(val1, six.integer_types):
        return val2

    return min(val1, val2)


def _add_media(dest, media):
    # Do what django.forms.Media.__add__() does without creating a new object.
    dest.add_css(media._css)
    dest.add_js(media._js)


def _is_template_updated(request, contentitem, cachekey):
    if not settings.DEBUG:
        return False
    # For debugging only: tell whether the template is updated,
    # so the cached values can be ignored.

    plugin = contentitem.plugin
    if _is_method_overwritten(plugin, ContentPlugin, 'get_render_template'):
        # oh oh, really need to fetch the real object.
        # Won't be needed that often.
        contentitem = contentitem.get_real_instance()  # Need to determine get_render_template(), this is only done with DEBUG=True
        template_names = plugin.get_render_template(request, contentitem)
    else:
        template_names = plugin.render_template

    if not template_names:
        return False
    if isinstance(template_names, six.string_types):
        template_names = [template_names]

    # With TEMPLATE_DEBUG = True, each node tracks it's origin.
    template = select_template(template_names)
    if TemplateAdapter is not None and isinstance(template, TemplateAdapter):
        # Django 1.8 template wrapper
        template_filename = template.origin.name
    else:
        node0 = template.nodelist[0]
        attr = 'source' if hasattr(node0, 'source') else 'origin'  # attribute depends on object type

        try:
            template_filename = getattr(node0, attr)[0].name
        except (AttributeError, IndexError):
            return False

    cache_stat = cache.get(cachekey + ".debug-stat")
    current_stat = os.path.getmtime(template_filename)
    if cache_stat != current_stat:
        cache.set(cachekey + ".debug-stat", current_stat)
        return True


def _is_method_overwritten(object, cls, method_name):
    # This is the easiest Python 2+3 compatible way to check if something was overwritten,
    # assuming that it always happens in a different package (which it does in our case).
    # This avoids the differences with im_func, or __func__ not being available.
    #
    # This worked in 2.7:
    #   object.get_render_template.__func__ is not cls.get_render_template.__func__
    #
    # This worked in 3.2 and 3.3:
    #   object.get_render_template.__func__ is not cls.get_render_template
    #
    # This all fails in 3.4, so just checking the __module__ instead.
    method = getattr(object, method_name)
    cls_method = getattr(cls, method_name)
    return method.__module__ != cls_method.__module__
