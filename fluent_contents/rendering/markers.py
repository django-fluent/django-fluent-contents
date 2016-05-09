"""
Draft - Internal functions for an "frontend edit mode".
"""
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe


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


def wrap_placeholder_output(html, placeholder):
    return mark_safe('<div class="cp-editable-placeholder" id="cp-editable-placeholder-{slot}" data-placeholder-id="{id}" data-placeholder-slot="{slot}">' \
           '{html}' \
           '</div>\n'.format(
        html=conditional_escape(html),
        id=placeholder.id,
        slot=placeholder.slot,
    ))


def wrap_anonymous_output(html):
    return mark_safe('<div class="cp-editable-placeholder">' \
           '{html}' \
           '</div>\n'.format(
        html=conditional_escape(html),
    ))


def wrap_contentitem_output(html, contentitem):
    return mark_safe('<div class="cp-editable-contentitem" data-itemtype="{itemtype}" data-item-id="{id}">' \
           '{html}' \
           '</div>\n'.format(
        html=conditional_escape(html),
        itemtype=contentitem.__class__.__name__,  # Same as ContentPlugin.type_name
        id=contentitem.id,
    ))
