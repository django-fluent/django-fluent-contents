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
from django.forms import Media
from django.utils import six
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


    def __init__(self, slot, title=None, role=None):
        """
        Create the placeholder data with a slot, and optional title and role.
        """
        if not slot:
            raise ValueError("Slot not defined for placeholder!")

        self.slot = slot
        self.title = title or self.slot
        self.role = self.ROLE_ALIASES.get(role, role or Placeholder.MAIN)

        # Ensure upfront value checking
        allows_roles = dict(Placeholder.ROLES).keys()
        if self.role not in allows_roles:
            raise ValueError("Invalid role '{0}' for placeholder '{1}': allowed are: {2}.".format(self.role, self.title or self.slot, ', '.join(self.ROLE_ALIASES.keys())))


    def as_dict(self):
        """
        Return the contents as dictionary, for initial form data.
        The dictionary contains the fields:

        * ``slot``
        * ``title``
        * ``role``
        """
        return {
            'slot': self.slot,
            'title': self.title,
            'role': self.role
        }


    def __repr__(self):
        return '<{0}: slot={1} role={2} title={3}>'.format(self.__class__.__name__, self.slot, self.role, self.title)


class ContentItemOutput(SafeData):
    """
    A wrapper with holds the rendered output of a plugin,
    This object is returned by the :func:`~fluent_contents.rendering.render_placeholder`
    and :func:`ContentPlugin.render() <fluent_contents.extensions.ContentPlugin.render>` method.

    Instances can be treated like a string object,
    but also allows reading the :attr:`html` and :attr:`media` attributes.
    """
    def __init__(self, html, media=None):
        self.html = conditional_escape(html)  # enforce consistency
        self.media = media or ImmutableMedia.empty_instance

    # Pretend to be a string-like object.
    # Both makes the caller easier to use, and keeps compatibility with 0.9 code.
    def __unicode__(self):
        return unicode(self.html)

    def __len__(self):
        return len(unicode(self.html))

    if six.PY3:
        def __str__(self):
            return self.__unicode__()
    else:
        def __str__(self):
            return self.__unicode__().encode('utf-8')

    def __repr__(self):
        return "<PluginOutput '{0}'>".format(repr(self.html))

    def __getattr__(self, item):
        return getattr(self.html, item)

    def __getitem__(self, item):
        return unicode(self).__getitem__(item)

    def __getstate__(self):
        return (unicode(self.html), self.media._css, self.media._js)

    def __setstate__(self, state):
        # Handle pickling manually, otherwise invokes __getattr__ in a loop.
        # (the first call goes to __setstate__, while self.html isn't set so __getattr__ is invoked again)
        html_str, css, js = state
        self.html = mark_safe(html_str)

        if not css and not js:
            self.media = ImmutableMedia.empty_instance
        else:
            self.media = ImmutableMedia()
            self.media._css = css
            self.media._js = js


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

ImmutableMedia.empty_instance = ImmutableMedia()
