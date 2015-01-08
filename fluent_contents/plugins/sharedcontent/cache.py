"""
Cache key retrieval.
"""
from fluent_contents.cache import get_placeholder_cache_key_for_parent


def get_shared_content_cache_key_ptr(site_id, slug):
    """
    Get the rendering cache key for a sharedcontent block.

    This key is an indirection for the actual cache key,
    which is based on the object ID and parent ID.
    """
    return "sharedcontent_key.{0}.{1}".format(site_id, slug)


def get_shared_content_cache_key(sharedcontent):
    # Generate the key that render_placeholder() would use to store all output in.
    return get_placeholder_cache_key_for_parent(sharedcontent, 'shared_content', sharedcontent.language_code)
