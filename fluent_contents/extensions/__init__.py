"""
Special classes to extend the module; e.g. plugins.

The extension mechanism is provided for projects that benefit
from a tighter integration then the Django URLconf can provide.

The API uses a registration system.
While plugins can be easily detected via ``__subclasses__()``, the register approach is less magic and more explicit.
Having to do an explicit register ensures future compatibility with other API's like reversion.
"""
from fluent_contents.forms import (  # Expose over here now, still leave at old location.
    ContentItemForm,
)
from fluent_contents.models import (  # Allow plugins to pick everything from 'extensions'
    ContentItem,
)

from .model_fields import PluginFileField, PluginHtmlField, PluginImageField, PluginUrlField
from .pluginbase import ContentPlugin, HttpRedirectRequest, PluginContext
from .pluginpool import PluginAlreadyRegistered, PluginNotFound, PluginPool, plugin_pool

__all__ = (
    "PluginContext",
    "ContentPlugin",
    "HttpRedirectRequest",
    "ContentItem",
    "PluginUrlField",
    "PluginFileField",
    "PluginImageField",
    "PluginHtmlField",
    "ContentItemForm",
    "plugin_pool",
    "PluginPool",
    "PluginNotFound",
    "PluginAlreadyRegistered",
)
