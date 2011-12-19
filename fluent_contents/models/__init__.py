from fluent_contents.models.db import Placeholder, ContentItem


class PlaceholderData(object):
    """
    A wrapper with data of a placeholder node.
    """
    ROLE_ALIASES = {
        'main': Placeholder.MAIN,
        'sidebar': Placeholder.SIDEBAR,
        'related': Placeholder.RELATED
    }

    def __init__(self, slot, title=None, role=None):
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
        """
        return {
            'slot': self.slot,
            'title': self.title,
            'role': self.role
        }


__all__ = ['Placeholder', 'ContentItem', 'PlaceholderData']
