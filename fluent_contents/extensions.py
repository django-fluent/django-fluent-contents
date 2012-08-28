"""
Special classes to extend the module; e.g. plugins.

The extension mechanism is provided for projects that benefit
from a tighter integration then the Django URLconf can provide.

The API uses a registration system.
While plugins can be easily detected via ``__subclasses__()``, the register approach is less magic and more explicit.
Having to do an explicit register ensures future compatibility with other API's like reversion.
"""
from django.conf import settings
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core import context_processors
from django.contrib.auth import context_processors as auth_context_processors
from django.contrib.messages import context_processors as messages_context_processors
from django.db import DatabaseError
from django.template.context import Context
from django.template.loader import render_to_string
from django.utils.html import linebreaks, escape
from django.utils.importlib import import_module
from django.utils.translation import ugettext as _
from fluent_contents.forms import ContentItemForm
from fluent_contents.models import ContentItem
from threading import Lock

__all__ = ('PluginContext', 'ContentPlugin', 'plugin_pool')


# This mechanism is mostly inspired by Django CMS,
# which nice job at defining a clear extension model.
# (c) Django CMS developers, BSD licensed.

# Some standard request processors to use in the plugins,
# Naturally, you want STATIC_URL to be available in plugins.

def _add_debug(request):
    return {'debug': settings.DEBUG}

_STANDARD_REQUEST_CONTEXT_PROCESSORS = (
    context_processors.request,
    context_processors.static,
    context_processors.csrf,
    context_processors.media,
    context_processors.i18n,
    auth_context_processors.auth,
    messages_context_processors.messages,
    _add_debug,
)


class PluginContext(Context):
    """
    A template Context class similar to :class:`~django.template.context.RequestContext`, that enters some pre-filled data.
    This ensures that variables such as ``STATIC_URL`` and ``request`` are available in the plugin templates.
    """
    def __init__(self, request, dict=None, current_app=None):
        # If there is any reason to site-global context processors for plugins,
        # I'd like to know the usecase, and it could be implemented here.
        Context.__init__(self, dict, current_app=current_app)
        for processor in _STANDARD_REQUEST_CONTEXT_PROCESSORS:
            self.update(processor(request))


class ContentPlugin(object):
    """
    The base class for all content plugins.

    A plugin defines the rendering for a :class:`~fluent_contents.models.ContentItem`, settings and presentation in the admin interface.
    To create a new plugin, derive from this class and call :func:`plugin_pool.register <PluginPool.register>` to enable it.
    For example:

    .. code-block:: python

        from fluent_contents.extensions import plugin_pool, ContentPlugin

        @plugin_pool.register
        class AnnouncementBlockPlugin(ContentPlugin):
            model = AnnouncementBlockItem
            render_template = "plugins/announcementblock.html"
            category = _("Simple blocks")

    As minimal configuration, specify the :attr:`model` and :attr:`render_template` fields.
    The :attr:`model` should be a subclass of the :class:`~fluent_contents.models.ContentItem` model class.

    .. note::
        When the plugin is registered in the :attr:`plugin_pool`, it will be instantiated only once.
        It is therefore not possible to store per-request state at the plugin object.
        This is similar to the behavior of the :class:`~django.contrib.admin.ModelAdmin` classes in Django.

    To customize the admin, the :attr:`admin_form_template`, :attr:`admin_form` can be defined,
    and a ``class Media`` can be included to provide extra CSS and JavaScript files for the admin interface.
    Some well known properties of the :class:`~django.contrib.admin.ModelAdmin` class can also be specified on plugins;
    such as the
    :attr:`~django.contrib.admin.ModelAdmin.raw_id_fields`,
    :attr:`~django.contrib.admin.ModelAdmin.fieldsets` and
    :attr:`~django.contrib.admin.ModelAdmin.readonly_fields` settings.

    The rendered output of a plugin is cached by default, assuming that most content is static.
    This also avoids extra database queries to retrieve the model objects.
    In case the plugin needs to output content dynamically, include ``cache_output = False`` in the plugin definition.
    """
    __metaclass__ = forms.MediaDefiningClass

    # -- Settings to override:

    #: The model to use, must derive from :class:`fluent_contents.models.ContentItem`.
    model = None

    #: The form to use in the admin interface. By default it uses a  :class:`fluent_contents.models.ContentItemForm`.
    form = ContentItemForm

    #: The template to render the admin interface with
    admin_form_template = "admin/fluent_contents/contentitem/admin_form.html"

    #: An optional template which is included in the admin interface, to initialize components (e.g. JavaScript)
    admin_init_template = None

    #: The fieldsets for the admin view.
    fieldsets = None

    #: The template to render the frontend HTML output.
    render_template = None

    #: By default, rendered output is cached, and updated on admin changes.
    cache_output = True

    #: The category to display the plugin at.
    category = None

    #: Alternative template for the view.
    ADMIN_TEMPLATE_WITHOUT_LABELS = "admin/fluent_contents/contentitem/admin_form_without_labels.html"

    #: The fields to display as raw ID
    raw_id_fields = ()

    #: The fields to display in a vertical filter
    filter_vertical = ()

    #: The fields to display in a horizontal filter
    filter_horizontal = ()

    #: The fields to display as radio choice
    radio_fields = {}

    #: Fields to automatically populate with values
    prepopulated_fields = {}

    #: Overwritten formfield attributes, e.g. the 'widget'. Allows both the class and fieldname as key.
    formfield_overrides = {}

    #: The fields to display as readonly.
    readonly_fields = ()


    def __init__(self):
        self._type_id = None


    def __repr__(self):
        return '<{0} for {1} model>'.format(self.__class__.__name__, unicode(self.model.__name__).encode('ascii'))


    @property
    def verbose_name(self):
        """
        The title for the plugin, by default it reads the ``verbose_name`` of the model.
        """
        return self.model._meta.verbose_name


    @property
    def type_name(self):
        """
        Return the classname of the model, this is mainly provided for templates.
        """
        return self.model.__name__


    @property
    def type_id(self):
        """
        Shortcut to retrieving the ContentType id of the model.
        """
        if self._type_id is None:
            try:
                self._type_id = ContentType.objects.get_for_model(self.model).id
            except DatabaseError as e:
                raise DatabaseError("Unable to fetch ContentType object, is a plugin being registered before the initial syncdb? (original error: {0})".format(str(e)))

        return self._type_id


    def get_model_instances(self):
        """
        Return the model instances the plugin has created.
        """
        return self.model.objects.all()


    def _render_contentitem(self, request, instance):
        # Internal wrapper for render(), to allow updating the method signature easily.
        # It also happens to really simplify code navigation.
        return self.render(request=request, instance=instance)


    def render(self, request, instance, **kwargs):
        """
        The rendering/view function that displays a plugin model instance.

        :param instance: An instance of the ``model`` the plugin uses.
        :param request: The Django :class:`~django.http.HttpRequest` class containing the request parameters.
        :param kwargs: An optional slot for any new parameters.

        To render a plugin, either override this function, or specify the :attr:`render_template` variable,
        and optionally override :func:`get_context`.
        It is recommended to wrap the output in a ``<div>`` tag,
        to prevent the item from being displayed right next to the previous plugin.

        To render raw HTML code, use :func:`~django.utils.safestring.mark_safe` on the returned HTML.
        """
        render_template = self.get_render_template(request, instance, **kwargs)
        if render_template:
            context = self.get_context(request, instance, **kwargs)
            return self.render_to_string(request, render_template, context)
        else:
            return unicode(_(u"{No rendering defined for class '%s'}" % self.__class__.__name__))


    def render_to_string(self, request, template, context, content_instance=None):
        """
        Render a custom template with the :class:`~PluginContext` as context instance.
        """
        if not content_instance:
            content_instance = PluginContext(request)
        return render_to_string(template, context, context_instance=content_instance)


    def render_error(self, error):
        """
        A default implementation to render an exception.
        """
        return '<div style="color: red; border: 1px solid red; padding: 5px;">' \
               '<p><strong>%s</strong></p>%s</div>' % (_('Error:'), linebreaks(escape(str(error))))


    def get_render_template(self, request, instance, **kwargs):
        """
        Return the template to render for the specific model `instance` or `request`,
        By default it uses the ``render_template`` attribute.
        """
        return self.render_template


    def get_context(self, request, instance, **kwargs):
        """
        Return the context to use in the template defined by ``render_template`` (or :func:`get_render_template`).
        By default, it returns the model instance as ``instance`` field in the template.
        """
        return {
            'instance': instance,
        }



# -------- Some utils --------

def _import_apps_submodule(submodule):
    """
    Look for a submodule is a series of packages, e.g. ".content_plugins" in all INSTALLED_APPS.
    """
    for app in settings.INSTALLED_APPS:
        try:
            import_module('.' + submodule, app)
        except ImportError, e:
            if submodule not in str(e):
                raise   # import error is a level deeper.
            else:
                pass


# -------- API to access plugins --------

class PluginAlreadyRegistered(Exception):
    """
    Raised when attemping to register a plugin twice.
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
        Make a plugin known by the CMS.

        :param plugin: The plugin class, deriving from :class:`ContentPlugin`.

        The plugin will be instantiated, just like Django does this with :class:`~django.contrib.admin.ModelAdmin` classes.
        If a plugin is already registered, this will raise a :class:`PluginAlreadyRegistered` exception.
        """
        # Duck-Typing does not suffice here, avoid hard to debug problems by upfront checks.
        assert issubclass(plugin, ContentPlugin), "The plugin must inherit from `ContentPlugin`"
        assert plugin.model, "The plugin has no model defined"
        assert issubclass(plugin.model, ContentItem), "The plugin model must inherit from `ContentItem`"
        assert issubclass(plugin.form, ContentItemForm), "The plugin form must inherit from `ContentItemForm`"

        name = plugin.__name__
        if name in self.plugins:
            raise PluginAlreadyRegistered("{0}: a plugin with this name is already registered".format(name))
        name = name.lower()

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
        return self.plugins.values()


    def get_plugins_by_name(self, *names):
        """
        Return a list of plugins by plugin class, or name.
        """
        self._import_plugins()
        plugin_instances = []
        for name in names:
            if isinstance(name, basestring):
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
            raise PluginNotFound("No plugin found for content type '{0}'.".format(contenttype))
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
            _import_apps_submodule("content_plugins")
            self.detected = True
        finally:
            self.scanLock.release()

    def _setup_lazy_indexes(self):
        # The ContentType is not read yet at .register() time, since that enforces the database to exist at that time.
        # If a plugin library is imported via different paths that might not be the case when `./manage.py syncdb` runs.
        if self._name_for_ctype_id is None:
            plugin_ctypes = {}  # separate dict to build, thread safe
            self._import_plugins()
            for name, plugin in self.plugins.iteritems():
                plugin_ctypes[plugin.type_id] = name

            self._name_for_ctype_id = plugin_ctypes


#: The global plugin pool, a instance of the :class:`PluginPool` class.
plugin_pool = PluginPool()
