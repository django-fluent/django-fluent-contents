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
from fluent_contents.models.db import Placeholder, ContentItem
from fluent_contents.models.managers import PlaceholderManager, ContentItemManager, get_parent_lookup_kwargs
from fluent_contents.models.fields import PlaceholderField, PlaceholderRelation, ContentItemRelation

__all__ = (
    'Placeholder', 'ContentItem',
    'PlaceholderData',
    'PlaceholderManager', 'ContentItemManager', 'get_parent_lookup_kwargs',
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
