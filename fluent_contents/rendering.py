"""
This module provides functions to render placeholder content manually.
This can be used when the placeholder content is rendered outside of a template.
The templatetags also make use of these functions.
"""
from django.utils.safestring import mark_safe

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
        return "<!-- no items in placeholder '{0}' -->".format(placeholder.slot)
    else:
        return _render_items(request, items)


def render_content_items(request, items):
    """
    Render a list of :class:`~fluent_contents.models.ContentItem` objects as HTML string.
    """
    if not items:
        return "<!-- no items to render -->"
    else:
        return _render_items(request, items)


def _render_items(request, items):
    output = []
    for contentitem in items:
        plugin = contentitem.plugin
        output.append(plugin._render_contentitem(contentitem, request))

    return mark_safe(''.join(output))
