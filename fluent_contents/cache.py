"""
Functions for caching.
"""

def get_rendering_cache_key(placeholder_name, contentitem):
    """
    Return a cache key for the content item output
    """
    return "contentitem-@{0}-{1}-{2}".format(
        placeholder_name,
        contentitem.plugin.type_name,  # always returns the upcasted name.
        contentitem.id
    )
