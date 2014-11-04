"""
This module provides functions to render placeholder content manually.
Contents is cached in memcache whenever possible, only the remaining items are queried.
The templatetags also use these functions to render the :class:`~fluent_contents.models.ContentItem` objects.
"""
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
from fluent_contents import appsettings
from fluent_contents.cache import get_rendering_cache_key
from fluent_contents.extensions import PluginNotFound, ContentPlugin
from fluent_contents.models import ContentItemOutput, ImmutableMedia

# This code is separate from the templatetags,
# so it can be called outside the templates as well.
from parler.utils.context import smart_override

logger = logging.getLogger(__name__)



def render_placeholder(request, placeholder, parent_object=None, template_name=None, limit_parent_language=True, fallback_language=None):
    """
    Render a :class:`~fluent_contents.models.Placeholder` object.
    Returns a :class:`~fluent_contents.models.ContentItemOutput` object
    which contains the HTML output and :class:`~django.forms.Media` object.

    :param request: The current request object.
    :type request: :class:`~django.http.HttpRequest`
    :param placeholder: The placeholder object.
    :type placeholder: :class:`~fluent_contents.models.Placeholder`
    :param parent_object: Optional, the parent object of the placeholder (already implied by the placeholder)
    :param template_name: Optional template name used to concatenate the placeholder output.
    :type template_name: str
    :param limit_parent_language: Whether the items should be limited to the parent language.
    :type limit_parent_language: bool
    :param fallback_language: The fallback language to use if there are no items in the current language. Passing ``True`` uses the default :ref:`FLUENT_CONTENTS_DEFAULT_LANGUAGE_CODE`.
    :type fallback_language: bool/str
    :rtype: :class:`~fluent_contents.models.ContentItemOutput`
    """
    # Get the items
    items = placeholder.get_content_items(parent_object, limit_parent_language=limit_parent_language)
    if fallback_language and not items:
        language_code = appsettings.FLUENT_CONTENTS_DEFAULT_LANGUAGE_CODE if fallback_language is True else fallback_language
        items = placeholder.get_content_items(parent_object, limit_parent_language=False).translated(language_code)

    output = _render_items(request, placeholder, items, parent_object=parent_object, template_name=template_name)

    if is_edit_mode(request):
        output.html = _wrap_placeholder_output(output.html, placeholder)

    return output


def render_content_items(request, items, template_name=None):
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
    :rtype: :class:`~fluent_contents.models.ContentItemOutput`
    """
    if not items:
        output = ContentItemOutput(mark_safe(u"<!-- no items to render -->"))
    else:
        output = _render_items(request, None, items, parent_object=None, template_name=template_name)

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


def _render_items(request, placeholder, items, parent_object=None, template_name=None):
    edit_mode = is_edit_mode(request)
    item_output = {}
    output_ordering = []
    placeholder_cache_name = '@global@' if placeholder is None else placeholder.slot

    if not hasattr(items, "non_polymorphic"):
        # The items is either a list of manually created items, or it's a QuerySet.
        # Can't prevent reading the subclasses only, so don't bother with caching here.
        remaining_items = items
        output_ordering = [item.pk or id(item) for item in items]
    else:
        items = items.non_polymorphic()

        # First try to fetch all items non-polymorphic from memcache
        # If these are found, there is no need to query the derived data from the database.
        remaining_items = []
        for i, contentitem in enumerate(items):
            output_ordering.append(contentitem.pk)
            output = None
            try:
                # Respect the cache output setting of the plugin
                if appsettings.FLUENT_CONTENTS_CACHE_OUTPUT and contentitem.plugin.cache_output and contentitem.pk:
                    output = contentitem.plugin.get_cached_output(placeholder_cache_name, contentitem)

                    # Support transition to new output format.
                    if not isinstance(output, ContentItemOutput):
                        output = None
                        logger.debug("Flushed cached output of {0}#{1} to store new format (key: {2}) ".format(contentitem.plugin.type_name, contentitem.pk, placeholder_cache_name))
            except PluginNotFound:
                pass

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
        return ContentItemOutput(mark_safe(u"<!-- no items in placeholder '{0}' -->".format(escape(_get_placeholder_name(placeholder)))))
    elif remaining_items:
        # Render remaining items
        for contentitem in remaining_items:
            try:
                plugin = contentitem.plugin
            except PluginNotFound as e:
                output = ContentItemOutput(mark_safe(u'<!-- error: {0} -->\n'.format(str(e))))
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

                if appsettings.FLUENT_CONTENTS_CACHE_OUTPUT and plugin.cache_output and contentitem.pk:
                    contentitem.plugin.set_cached_output(placeholder_cache_name, contentitem, output)

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

    return ContentItemOutput(merged_output, merged_media)


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
    if plugin.get_render_template.__func__ is not ContentPlugin.get_render_template.__func__:
        # oh oh, really need to fetch the real object.
        # Won't be needed that often.
        contentitem = contentitem.get_real_instance()  # This is only needed with DEBUG=True
        template_names = plugin.get_render_template(request, contentitem)
    else:
        template_names = plugin.render_template

    if not template_names:
        return False
    if isinstance(template_names, six.string_types):
        template_names = [template_names]

    # With TEMPLATE_DEBUG = True, each node tracks it's origin.
    node0 = select_template(template_names).nodelist[0]
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
