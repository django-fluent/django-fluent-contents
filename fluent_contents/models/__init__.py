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
from future.builtins import str
from future.utils import python_2_unicode_compatible
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.forms import Media
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe, SafeData
from fluent_contents.models.db import Placeholder, ContentItem
from fluent_contents.models.managers import PlaceholderManager, ContentItemManager, get_parent_lookup_kwargs, get_parent_language_code
from fluent_contents.models.fields import PlaceholderField, PlaceholderRelation, ContentItemRelation

__all__ = (
    'Placeholder', 'ContentItem',
    'PlaceholderData', 'ContentItemOutput', 'ImmutableMedia',
    'PlaceholderManager', 'ContentItemManager', 'get_parent_lookup_kwargs', 'get_parent_language_code',
    'PlaceholderField', 'PlaceholderRelation', 'ContentItemRelation',
)

_ALLOWED_ROLES = list(dict(Placeholder.ROLES).keys())


class PlaceholderData(object):
    """
    A wrapper with data of a placeholder node.
    It shares the :attr:`slot`, :attr:`title` and :attr:`role` fields with the :class:`~fluent_contents.models.Placeholder` class.
    """
    ROLE_ALIASES = {
        'main': Placeholder.MAIN,
        'sidebar': Placeholder.SIDEBAR,
        'related': Placeholder.RELATED
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
            raise ValueError("Invalid role '{0}' for placeholder '{1}': allowed are: {2}.".format(self.role, self.title or self.slot, ', '.join(list(self.ROLE_ALIASES.keys()))))

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
            'slot': self.slot,
            'title': self.title,
            'role': self.role,
            'fallback_language': self.fallback_language,
            'allowed_plugins': [plugin.name for plugin in plugins],
        }

    def get_allowed_plugins(self):
        from fluent_contents import extensions
        return extensions.plugin_pool.get_allowed_plugins(self.slot)

    def __repr__(self):
        return '<{0}: slot={1} role={2} title={3}>'.format(self.__class__.__name__, self.slot, self.role, self.title)


@python_2_unicode_compatible
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
        return "<ContentItemOutput '{0}'>".format(repr(self.html))

    def __getattr__(self, item):
        return getattr(self.html, item)

    def __getitem__(self, item):
        return str(self).__getitem__(item)

    def __getstate__(self):
        return (str(self.html), self.media._css, self.media._js)

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
            self.media = ImmutableMedia()
            self.media._css = css
            self.media._js = js

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
        self._css = {}
        self._js = []

        if kwargs:
            Media.add_css(self, kwargs.get('css', None))
            Media.add_js(self, kwargs.get('js', None))

    def add_css(self, data):
        raise RuntimeError("Immutable media object")

    def add_js(self, data):
        raise RuntimeError("Immutable media object")

    def __add__(self, other):
        # Performance improvement
        if other is ImmutableMedia.empty_instance:
            return other

        # Fast copy
        combined = Media()
        combined._css = other._css.copy()
        combined._js = other._js[:]
        return combined


ImmutableMedia.empty_instance = ImmutableMedia()
