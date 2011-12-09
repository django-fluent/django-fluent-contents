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
    return render_placeholder_items(request, placeholder.slot, items)


def render_placeholder_items(request, slotname, items):
    """
    Render a list of placeholder items as HTML string.
    """
    if not items:
        return "<!-- no items in placeholder '{0}' -->".format(slotname)
    else:
        str = ''.join(contentitem.plugin._render_contentitem(contentitem, request) for contentitem in items)
        return mark_safe(str)
