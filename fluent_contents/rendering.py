"""
This module provides functions to render placeholder content manually.
Contents is cached in memcache whenever possible, only the remaining items are queried.
The templatetags also use these functions to render the :class:`~fluent_contents.models.ContentItem` objects.
"""
from django.core.cache import cache
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.utils.html import conditional_escape, escape
from django.utils.safestring import mark_safe
from fluent_contents import appsettings
from fluent_contents.cache import get_rendering_cache_key
from fluent_contents.extensions import PluginNotFound
import logging

# This code is separate from the templatetags,
# so it can be called outside the templates as well.

logger = logging.getLogger(__name__)


def render_placeholder(request, placeholder, parent_object=None, template_name=None):
    """
    Render a :class:`~fluent_contents.models.Placeholder` object as HTML string.
    """
    # Filter the items both by placeholder and parent;
    # this mimics the behavior of CMS pages.
    items = placeholder.get_content_items(parent_object)
    html = _render_items(request, placeholder.slot, items, template_name=template_name)

    if is_edit_mode(request):
        html = _wrap_placeholder_output(html, placeholder)
    return html


def render_content_items(request, items, template_name=None):
    """
    Render a list of :class:`~fluent_contents.models.ContentItem` objects as HTML string.
    """
    if not items:
        html = "<!-- no items to render -->"
    else:
        html = _render_items(request, '@global@', items, template_name=template_name)

    if is_edit_mode(request):
        html = _wrap_anonymous_output(html)
    return html


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


def _render_items(request, placeholder_name, items, template_name=None):
    edit_mode = is_edit_mode(request)
    output = {}
    output_ordering = []

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
            html = None
            try:
                # Respect the cache output setting of the plugin
                if contentitem.plugin.cache_output and contentitem.pk and appsettings.FLUENT_CONTENTS_CACHE_OUTPUT:
                    cachekey = get_rendering_cache_key(placeholder_name, contentitem)
                    html = cache.get(cachekey)
            except PluginNotFound:
                pass

            if html:
                output[contentitem.pk] = html
            else:
                remaining_items.append(contentitem)

        # Fetch derived table data for all objects not found in memcached
        if remaining_items:
            remaining_items = items.get_real_instances(remaining_items)

    # See if the queryset contained anything.
    # This test is moved here, to prevent earlier query execution.
    if not items:
        return u"<!-- no items in placeholder '{0}' -->".format(escape(placeholder_name))
    elif remaining_items:
        # Render remaining items
        for contentitem in remaining_items:
            try:
                plugin = contentitem.plugin
            except PluginNotFound as e:
                html = '<!-- error: {0} -->\n'.format(str(e))
            else:
                # Plugin output is likely HTML, but it should be placed in mark_safe() to raise awareness about escaping.
                # This is just like Django's Input.render() and unlike Node.render().
                html = conditional_escape(plugin._render_contentitem(request, contentitem))

                if plugin.cache_output and contentitem.pk and appsettings.FLUENT_CONTENTS_CACHE_OUTPUT:
                    cachekey = get_rendering_cache_key(placeholder_name, contentitem)
                    cache.set(cachekey, html)

                if edit_mode:
                    html = _wrap_contentitem_output(html, contentitem)

            output[contentitem.pk or id(contentitem)] = html

    # Order all rendered items in the correct sequence.  The derived tables should be truncated/reset,
    # so the base class model indexes don't necessary match with the derived indexes.
    output_ordered = []
    for pk in output_ordering:
        try:
            output_ordered.append(output[pk])
        except KeyError:
            # NOTE: if a table is truncated/reset, the base class still exists and causes a query to happen every time.
            item = [item for item in items if item.pk == pk][0]
            logger.warning("Missing derived model for ContentItem #{id}: {cls}.".format(id=pk, cls=item.plugin.type_name))
            pass

    # Combine all rendered items. Allow rendering the items with a template,
    # to inserting seperators or nice start/end code.
    if not template_name:
        return mark_safe(''.join(output_ordered))
    else:
        context = {
            'contentitems': zip(items, output_ordered),
            'edit_mode': edit_mode,
        }
        return render_to_string(template_name, context, context_instance=RequestContext(request))


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
