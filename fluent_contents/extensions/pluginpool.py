"""
Internal module for the plugin system,
the API is exposed via __init__.py
"""
import six
from django.core.exceptions import ImproperlyConfigured

from future.builtins import str
from threading import Lock
from django.contrib.contenttypes.models import ContentType
from fluent_contents import appsettings
from fluent_contents.forms import ContentItemForm
from fluent_contents.models import ContentItem
from fluent_utils.load import import_apps_submodule
from .pluginbase import ContentPlugin


__all__ = ('PluginContext', 'ContentPlugin', 'plugin_pool')


# This mechanism is mostly inspired by Django CMS,
# which nice job at defining a clear extension model.
# (c) Django CMS developers, BSD licensed.

# Some standard request processors to use in the plugins,
# Naturally, you want STATIC_URL to be available in plugins.


class PluginAlreadyRegistered(Exception):
    """
    Raised when attemping to register a plugin twice.
    """
    pass


class ModelAlreadyRegistered(Exception):
    """
    The model is already registered with another plugin.
    """
    pass


class PluginNotFound(Exception):
    """
    Raised when the plugin could not be found in the rendering process.
    """
    pass


class PluginPool(object):
    """
    The central administration of plugins.
    """
    scanLock = Lock()

    def __init__(self):
        self.plugins = {}
        self._name_for_model = {}
        self._name_for_ctype_id = None
        self.detected = False

    def register(self, plugin):
        """
        Make a plugin known to the CMS.

        :param plugin: The plugin class, deriving from :class:`ContentPlugin`.
        :type plugin: :class:`ContentPlugin`

        The plugin will be instantiated once, just like Django does this with :class:`~django.contrib.admin.ModelAdmin` classes.
        If a plugin is already registered, this will raise a :class:`PluginAlreadyRegistered` exception.
        """
        # Duck-Typing does not suffice here, avoid hard to debug problems by upfront checks.
        assert issubclass(plugin, ContentPlugin), "The plugin must inherit from `ContentPlugin`"
        assert plugin.model, "The plugin has no model defined"
        assert issubclass(plugin.model, ContentItem), "The plugin model must inherit from `ContentItem`"
        assert issubclass(plugin.form, ContentItemForm), "The plugin form must inherit from `ContentItemForm`"

        name = plugin.__name__  # using class here, no instance created yet.
        name = name.lower()
        if name in self.plugins:
            raise PluginAlreadyRegistered("{0}: a plugin with this name is already registered".format(name))

        # Avoid registering 2 plugins to the exact same model. If you want to reuse code, use proxy models.
        if plugin.model in self._name_for_model:
            # Having 2 plugins for one model breaks ContentItem.plugin and the frontend code
            # that depends on using inline-model names instead of plugins. Good luck fixing that.
            # Better leave the model==plugin dependency for now.
            existing_plugin = self.plugins[self._name_for_model[plugin.model]]
            raise ModelAlreadyRegistered("Can't register the model {0} to {2}, it's already registered to {1}!".format(
                plugin.model.__name__,
                existing_plugin.name,
                plugin.__name__
            ))

        # Make a single static instance, similar to ModelAdmin.
        plugin_instance = plugin()
        self.plugins[name] = plugin_instance
        self._name_for_model[plugin.model] = name       # Track reverse for model.plugin link

        # Only update lazy indexes if already created
        if self._name_for_ctype_id is not None:
            self._name_for_ctype_id[plugin.type_id] = name

        return plugin  # Allow decorator syntax

    def get_plugins(self):
        """
        Return the list of all plugin instances which are loaded.
        """
        self._import_plugins()
        return list(self.plugins.values())

    def get_allowed_plugins(self, placeholder_slot):
        """
        Return the plugins which are supported in the given placeholder name.
        """
        # See if there is a limit imposed.
        slot_config = appsettings.FLUENT_CONTENTS_PLACEHOLDER_CONFIG.get(placeholder_slot) or {}
        plugins = slot_config.get('plugins')
        if not plugins:
            return self.get_plugins()
        else:
            try:
                return self.get_plugins_by_name(*plugins)
            except PluginNotFound as e:
                raise PluginNotFound(str(e) + " Update the plugin list of the FLUENT_CONTENTS_PLACEHOLDER_CONFIG['{0}'] setting.".format(placeholder_slot))

    def get_plugins_by_name(self, *names):
        """
        Return a list of plugins by plugin class, or name.
        """
        self._import_plugins()
        plugin_instances = []
        for name in names:
            if isinstance(name, six.string_types):
                try:
                    plugin_instances.append(self.plugins[name.lower()])
                except KeyError:
                    raise PluginNotFound("No plugin named '{0}'.".format(name))
            elif issubclass(name, ContentPlugin):
                # Will also allow classes instead of strings.
                plugin_instances.append(self.plugins[self._name_for_model[name.model]])
            else:
                raise TypeError("get_plugins_by_name() expects a plugin name or class, not: {0}".format(name))
        return plugin_instances

    def get_model_classes(self):
        """
        Return all :class:`~fluent_contents.models.ContentItem` model classes which are exposed by plugins.
        """
        self._import_plugins()
        return [plugin.model for plugin in self.plugins.values()]

    def get_plugin_by_model(self, model_class):
        """
        Return the corresponding plugin for a given model.

        You can also use the :attr:`ContentItem.plugin <fluent_contents.models.ContentItem.plugin>` property directly.
        This is the low-level function that supports that feature.
        """
        self._import_plugins()                       # could happen during rendering that no plugin scan happened yet.
        assert issubclass(model_class, ContentItem)  # avoid confusion between model instance and class here!

        try:
            name = self._name_for_model[model_class]
        except KeyError:
            raise PluginNotFound("No plugin found for model '{0}'.".format(model_class.__name__))
        return self.plugins[name]

    def _get_plugin_by_content_type(self, contenttype):
        self._import_plugins()
        self._setup_lazy_indexes()

        ct_id = contenttype.id if isinstance(contenttype, ContentType) else int(contenttype)
        try:
            name = self._name_for_ctype_id[ct_id]
        except KeyError:
            # ContentType not found, likely a plugin is no longer registered or the app has been removed.
            try:
                # ContentType could be stale
                ct = contenttype if isinstance(contenttype, ContentType) else ContentType.objects.get_for_id(ct_id)
            except AttributeError:  # should return the stale type but Django <1.6 raises an AttributeError in fact.
                ct_name = 'stale content type'
            else:
                ct_name = '{0}.{1}'.format(ct.app_label, ct.model)
            raise PluginNotFound("No plugin found for content type #{0} ({1}).".format(contenttype, ct_name))

        return self.plugins[name]

    def _import_plugins(self):
        """
        Internal function, ensure all plugin packages are imported.
        """
        if self.detected:
            return

        # In some cases, plugin scanning may start during a request.
        # Make sure there is only one thread scanning for plugins.
        self.scanLock.acquire()
        if self.detected:
            return  # previous threaded released + completed

        try:
            import_apps_submodule("content_plugins")
            self.detected = True
        finally:
            self.scanLock.release()

    def _setup_lazy_indexes(self):
        # The ContentType is not read yet at .register() time, since that enforces the database to exist at that time.
        # If a plugin library is imported via different paths that might not be the case when `./manage.py syncdb` runs.
        if self._name_for_ctype_id is None:
            plugin_ctypes = {}  # separate dict to build, thread safe
            self._import_plugins()
            for name, plugin in self.plugins.items():
                ct_id = plugin.type_id
                if ct_id in plugin_ctypes:
                    raise ImproperlyConfigured("The plugin '{0}' returns the same type_id as the '{1}' plugin does".format(
                        plugin.name, plugin_ctypes[ct_id]
                    ))
                plugin_ctypes[ct_id] = name

            self._name_for_ctype_id = plugin_ctypes


#: The global plugin pool, a instance of the :class:`PluginPool` class.
plugin_pool = PluginPool()
