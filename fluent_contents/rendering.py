"""
This module provides functions to render placeholder content manually.
This can be used when the placeholder content is rendered outside of a template.
The templatetags also make use of these functions.
"""
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from fluent_contents.extensions import PluginNotFound

# This code is separate from the templatetags,
# so it can be called outside the templates as well.


def render_placeholder(request, placeholder, parent_object=None):
    """
    Render a :class:`~fluent_contents.models.Placeholder` object as HTML string.
    """
    # Filter the items both by placeholder and parent;
    # this mimics the behavior of CMS pages.
    items = placeholder.get_content_items(parent_object)

    if not items:
        html = "<!-- no items in placeholder '{0}' -->".format(placeholder.slot)
    else:
        html = _render_items(request, items)

    if is_edit_mode(request):
        html = _wrap_placeholder_output(html, placeholder)
    return html


def render_content_items(request, items):
    """
    Render a list of :class:`~fluent_contents.models.ContentItem` objects as HTML string.
    """
    if not items:
        html ="<!-- no items to render -->"
    else:
        html = _render_items(request, items)

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
    Return whether edit mode is enabled.
    """
    return getattr(request, '_fluent_contents_edit_mode', False)


def _render_items(request, items):
    edit_mode = is_edit_mode(request)

    output = []
    for contentitem in items:
        try:
            plugin = contentitem.plugin
        except PluginNotFound as e:
            html = '<!-- error: {0} -->\n'.format(str(e))
        else:
            # Plugin output is likely HTML, but it should be placed in mark_safe() to raise awareness about escaping.
            # This is just like Input.render() and unlike Node.render().
            html = conditional_escape(plugin._render_contentitem(request, contentitem))

        if edit_mode:
            html = _wrap_contentitem_output(html, contentitem)
        output.append(html)

    return mark_safe(''.join(output))


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
