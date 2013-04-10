"""
Special classes to extend the module; e.g. plugins.

The extension mechanism is provided for projects that benefit
from a tighter integration then the Django URLconf can provide.

The API uses a registration system.
While plugins can be easily detected via ``__subclasses__()``, the register approach is less magic and more explicit.
Having to do an explicit register ensures future compatibility with other API's like reversion.
"""
from .pluginbase import PluginContext, ContentPlugin
from .pluginpool import plugin_pool, PluginNotFound, PluginAlreadyRegistered
from fluent_contents.forms import ContentItemForm   # Expose over here now, still leave at old location.
from fluent_contents.models import ContentItem      # Allow plugins to pick everything from 'extensions'


__all__ = (
    'PluginContext', 'ContentPlugin',
    'ContentItem',
    'ContentItemForm',
    'plugin_pool',
    'PluginNotFound', 'PluginAlreadyRegistered',
)
