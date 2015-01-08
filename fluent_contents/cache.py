"""
Functions for caching.
"""
from django.contrib.contenttypes.models import ContentType


def get_rendering_cache_key(placeholder_name, contentitem):
    """
    Return a cache key for the content item output.

    .. seealso::

        The :func:`ContentItem.clear_cache() <fluent_contents.models.ContentItem.clear_cache>` function
        can be used to remove the cache keys of a retrieved object.
    """
    if not contentitem.pk:
        return None
    return "contentitem.@{0}.{1}.{2}".format(
        placeholder_name,
        contentitem.plugin.type_name,  # always returns the upcasted name.
        contentitem.pk,                # already unique per language_code
    )


def get_placeholder_cache_key(placeholder, language_code):
    """
    Return a cache key for an existing placeholder object.

    This key is used to cache the entire output of a placeholder.
    """
    return _get_placeholder_cache_key_for_id(
        placeholder.parent_type_id,
        placeholder.parent_id,
        placeholder.slot,
        language_code
    )


def get_placeholder_cache_key_for_parent(parent_object, placeholder_name, language_code):
    """
    Return a cache key for a placeholder.

    This key is used to cache the entire output of a placeholder.
    """
    parent_type = ContentType.objects.get_for_model(parent_object)
    return _get_placeholder_cache_key_for_id(
        parent_type.id,
        parent_object.pk,
        placeholder_name,
        language_code
    )


def _get_placeholder_cache_key_for_id(parent_type_id, parent_id, placeholder_name, language_code):
    # Return a cache key for a placeholder, without having to fetch a placeholder first.
    # Not yet exposed, maybe more object values are needed later.
    return "placeholder.{0}.{1}.{2}.{3}".format(parent_type_id, parent_id, placeholder_name, language_code)
