from content_placeholders.models.db import Placeholder, ContentItem


class PlaceholderData(object):
    """
    A wrapper with data of a placeholder node.
    """
    def __init__(self, slot, title=None):
        self.slot = slot
        self.title = title or slot


__all__ = ['Placeholder', 'ContentItem', 'PlaceholderData']
