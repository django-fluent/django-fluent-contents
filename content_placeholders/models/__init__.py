from content_placeholders.models.db import Placeholder, ContentItem


class PlaceholderData(object):
    """
    A wrapper with data of a placeholder node.
    """
    def __init__(self, slot, title=None):
        self.slot = slot
        self.title = title or slot

    def as_dict(self):
        """
        Return the contents as dictionary, for initial form data.
        """
        return {
            'slot': self.slot,
            'title': self.title
        }


__all__ = ['Placeholder', 'ContentItem', 'PlaceholderData']
