from django.forms import Media

from fluent_contents.models import ImmutableMedia

from .utils import add_media


def register_frontend_media(request, media):
    """
    Add a :class:`~django.forms.Media` class to the current request.
    This will be rendered by the ``render_plugin_media`` template tag.
    """
    if media is ImmutableMedia.empty_instance:
        return

    if not hasattr(request, "_fluent_contents_frontend_media"):
        request._fluent_contents_frontend_media = Media()

    add_media(request._fluent_contents_frontend_media, media)


def get_frontend_media(request):
    """
    Return the media that was registered in the request object.

    .. note::
        The output of plugins is typically cached. Changes the the
        registered media only show up after flushing the cache,
        or re-saving the items (which flushes the cache).
    """
    return (
        getattr(request, "_fluent_contents_frontend_media", None) or ImmutableMedia.empty_instance
    )
