"""
Functions for caching.
"""

def get_rendering_cache_key(placeholder_name, contentitem):
    """
    Return a cache key for the content item output.

    .. seealso::

        The :func:`ContentItem.clear_cache() <fluent_contents.models.ContentItem.clear_cache>` function
        can be used to remove the cache keys of a retrieved object.
    """
    if not contentitem.pk:
        return None
    return "contentitem-@{0}-{1}-{2}".format(
        placeholder_name,
        contentitem.plugin.type_name,  # always returns the upcasted name.
        contentitem.pk
    )
