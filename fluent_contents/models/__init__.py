"""
The `fluent_contents` package defines two models, for storing the content data:

* :class:`Placeholder`
* :class:`ContentItem`

Secondly, there are a few possible fields to add to parent models:

* :class:`PlaceholderField`
* :class:`PlaceholderRelation`
* :class:`ContentItemRelation`

Finally, to exchange template data, a :class:`PlaceholderData` object is available
which mirrors the relevant fields of the :class:`Placeholder` model.
"""
import django
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.forms import Media
from django.utils.html import conditional_escape
from django.utils.safestring import SafeData, mark_safe

from fluent_contents.models.db import ContentItem, Placeholder
from fluent_contents.models.fields import (
    ContentItemRelation,
    PlaceholderField,
    PlaceholderRelation,
)
from fluent_contents.models.managers import (
    ContentItemManager,
    PlaceholderManager,
    get_parent_language_code,
    get_parent_lookup_kwargs,
)

__all__ = (
    "Placeholder",
    "ContentItem",
    "PlaceholderData",
    "ContentItemOutput",
    "ImmutableMedia",
    "PlaceholderManager",
    "ContentItemManager",
    "get_parent_lookup_kwargs",
    "get_parent_language_code",
    "PlaceholderField",
    "PlaceholderRelation",
    "ContentItemRelation",
)

_ALLOWED_ROLES = list(dict(Placeholder.ROLES).keys())


class PlaceholderData:
    """
    A wrapper with data of a placeholder node.
    It shares the :attr:`slot`, :attr:`title` and :attr:`role` fields with the :class:`~fluent_contents.models.Placeholder` class.
    """

    ROLE_ALIASES = {
        "main": Placeholder.MAIN,
        "sidebar": Placeholder.SIDEBAR,
        "related": Placeholder.RELATED,
    }

    def __init__(self, slot, title=None, role=None, fallback_language=None):
        """
        Create the placeholder data with a slot, and optional title and role.
        """
        if not slot:
            raise ValueError("Slot not defined for placeholder!")

        self.slot = slot
        self.title = title or self.slot
        self.role = self.ROLE_ALIASES.get(role, role or Placeholder.MAIN)
        self.fallback_language = fallback_language or None

        # Ensure upfront value checking
        if self.role not in _ALLOWED_ROLES:
            raise ValueError(
                "Invalid role '{}' for placeholder '{}': allowed are: {}.".format(
                    self.role,
                    self.title or self.slot,
                    ", ".join(list(self.ROLE_ALIASES.keys())),
                )
            )

    def as_dict(self):
        """
        Return the contents as dictionary, for client-side export.
        The dictionary contains the fields:

        * ``slot``
        * ``title``
        * ``role``
        * ``fallback_language``
        * ``allowed_plugins``
        """
        plugins = self.get_allowed_plugins()
        return {
            "slot": self.slot,
            "title": self.title,
            "role": self.role,
            "fallback_language": self.fallback_language,
            "allowed_plugins": [plugin.name for plugin in plugins],
        }

    def get_allowed_plugins(self):
        from fluent_contents import extensions

        return extensions.plugin_pool.get_allowed_plugins(self.slot)

    def __repr__(self):
        return "<{}: slot={} role={} title={}>".format(
            self.__class__.__name__, self.slot, self.role, self.title
        )


class ContentItemOutput(SafeData):
    """
    A wrapper with holds the rendered output of a plugin,
    This object is returned by the :func:`~fluent_contents.rendering.render_placeholder`
    and :func:`ContentPlugin.render() <fluent_contents.extensions.ContentPlugin.render>` method.

    Instances can be treated like a string object,
    but also allows reading the :attr:`html` and :attr:`media` attributes.
    """

    def __init__(self, html, media=None, cacheable=True, cache_timeout=DEFAULT_TIMEOUT):
        self.html = conditional_escape(html)  # enforce consistency
        self.media = media or ImmutableMedia.empty_instance
        # Mainly used internally for the _render_items():
        # NOTE: this is the only place where 'cachable' was written was 'cacheable'
        self.cacheable = cacheable
        self.cache_timeout = cache_timeout or DEFAULT_TIMEOUT

    # Pretend to be a string-like object.
    # Both makes the caller easier to use, and keeps compatibility with 0.9 code.
    def __str__(self):
        return str(self.html)

    def __len__(self):
        return len(str(self.html))

    def __repr__(self):
        return f"<ContentItemOutput '{repr(self.html)}'>"

    def __getattr__(self, item):
        return getattr(self.html, item)

    def __getitem__(self, item):
        return str(self).__getitem__(item)

    def __getstate__(self):
        return (str(self.html), self.media._css_lists, self.media._js_lists)

    def __setstate__(self, state):
        # Handle pickling manually, otherwise invokes __getattr__ in a loop.
        # (the first call goes to __setstate__, while self.html isn't set so __getattr__ is invoked again)
        html_str, css, js = state
        self.html = mark_safe(html_str)
        self.cacheable = True  # Implied by retrieving from cache.
        self.cache_timeout = DEFAULT_TIMEOUT

        if not css and not js:
            self.media = ImmutableMedia.empty_instance
        else:
            if isinstance(css, dict):
                # cache from 2.1 version, convert to lists
                self.media = Media(css=css, js=js)
            else:
                self.media = Media()
                self.media._css_lists = css
                self.media._js_lists = js

    def _insert_media(self, media):
        """
        Insert more media files to the output. (internal-private for now).
        """
        # Upgrade the performance-optimization of ImmediateMedia to an editable object.
        if self.media is ImmutableMedia.empty_instance:
            self.media = Media() + media
        else:
            # Needs to be merged as new copy, can't risk merging the 'media' object
            self.media = media + self.media


# Avoid continuous construction of Media objects.

class ImmutableMedia(Media):
    #: The empty object (a shared instance of this class)
    empty_instance = None

    def __init__(self, **kwargs):
        if kwargs:
            # This wasn't used internally at all, but check if any third party packages did this.
            raise ValueError(
                "Providing css/js to ImmutableMedia is no longer supported on Django 2.2+"
            )
        super().__init__()

    def __add__(self, other):
        # Django 2.2 no longer provides add_js/add_css,
        # making the Media object behave as immutable.
        # 'other' could also be ImmutableMedia.empty_instance
        return other




ImmutableMedia.empty_instance = ImmutableMedia()
