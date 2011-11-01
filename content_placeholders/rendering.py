"""
Rendering of placeholder tags.
"""
from django.utils.safestring import mark_safe

# This code is separate from the templatetags,
# so it can be called outside the templates as well.


def render_placeholder(request, placeholder):
    """
    Render a placeholder as HTML string.
    """
    return render_placeholder_items(request, placeholder.slot, placeholder.contentitems.all())


def render_placeholder_items(request, slotname, items):
    """
    Render a list of placeholder items as HTML string.
    """
    if not items:
        return "<!-- no items in placeholder '{0}' -->".format(slotname)
    else:
        str = ''.join(contentitem.plugin._render_contentitem(contentitem, request) for contentitem in items)
        return mark_safe(str)
