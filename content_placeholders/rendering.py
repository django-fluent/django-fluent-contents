"""
Rendering of placeholder tags.
"""
from django.utils.safestring import mark_safe

# This code is separate from the templatetags,
# so it can be called outside the templates as well.


def render_placeholder(request, placeholder, parent_object=None):
    """
    Render a placeholder as HTML string.
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
    Render a list of placeholder items as HTML string.
    """
    if not items:
        return "<!-- no items in placeholder -->"
    else:
        return _render_items(request, items)


def _render_items(request, items):
    str = ''.join(contentitem.plugin._render_contentitem(contentitem, request) for contentitem in items)
    return mark_safe(str)
