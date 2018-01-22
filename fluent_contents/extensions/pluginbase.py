"""
Internal module for the plugin system,
the API is exposed via __init__.py
"""
import django.contrib.auth.context_processors
import django.contrib.messages.context_processors
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect
from future.builtins import str
from future.utils import with_metaclass
from django.conf import settings
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.db import DatabaseError
from django.forms import Media, MediaDefiningClass
from django.template import context_processors
from django.template.context import Context
from django.template.loader import render_to_string
from django.utils.html import linebreaks, escape
from django.utils.translation import ugettext_lazy as _, get_language
from fluent_contents.cache import get_rendering_cache_key, get_placeholder_cache_key
from fluent_contents.forms import ContentItemForm
from fluent_contents.models import ContentItemOutput, ImmutableMedia, DEFAULT_TIMEOUT
from fluent_contents.utils.search import get_search_field_values, clean_join


# Some standard request processors to use in the plugins,
# Naturally, you want STATIC_URL to be available in plugins.
def _add_debug(request):
    return {'debug': settings.DEBUG}


_STANDARD_REQUEST_CONTEXT_PROCESSORS = (
    context_processors.csrf,
    context_processors.debug,
    context_processors.i18n,
    context_processors.media,
    context_processors.request,
    context_processors.static,
    django.contrib.auth.context_processors.auth,
    django.contrib.messages.context_processors.messages,
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
        if current_app is None:
            # Avoid RemovedInDjango110Warning
            Context.__init__(self, dict)
        else:
            Context.__init__(self, dict, current_app=current_app)

        for processor in _STANDARD_REQUEST_CONTEXT_PROCESSORS:
            self.update(processor(request))


def frontend_media_property(cls):
    # Identical to the media_property, adapted to read the "FrontendMedia" class
    # and optimized to avoid useless object creation.

    def _media(self):
        # Get the media property of the superclass, if it exists
        sup_cls = super(cls, self)
        try:
            base = sup_cls.frontend_media
        except AttributeError:
            base = ImmutableMedia.empty_instance

        # Get the media definition for this class
        definition = getattr(cls, 'FrontendMedia', None)
        if definition:
            media = Media(definition)

            # Not supporting extend=('js',) here, not documented in Django either.
            if getattr(definition, 'extend', True) and base is not ImmutableMedia.empty_instance:
                return base + media

            return media
        else:
            return base
    return property(_media)


class PluginMediaDefiningClass(MediaDefiningClass):
    "Metaclass for classes that can have media definitions"
    def __new__(cls, name, bases, attrs):
        new_class = super(PluginMediaDefiningClass, cls).__new__(cls, name, bases, attrs)
        if 'frontend_media' not in attrs and 'FrontendMedia' in attrs:
            new_class.frontend_media = frontend_media_property(new_class)
        return new_class


class ContentPlugin(with_metaclass(PluginMediaDefiningClass, object)):
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

    To customize the admin, the :attr:`admin_form_template` and :attr:`form` can be defined.
    Some well known properties of the :class:`~django.contrib.admin.ModelAdmin` class can also be specified on plugins;
    such as:

    * :attr:`~django.contrib.admin.ModelAdmin.fieldsets`
    * :attr:`~django.contrib.admin.ModelAdmin.filter_horizontal`
    * :attr:`~django.contrib.admin.ModelAdmin.filter_vertical`
    * :attr:`~django.contrib.admin.ModelAdmin.prepopulated_fields`
    * :attr:`~django.contrib.admin.ModelAdmin.radio_fields`
    * :attr:`~django.contrib.admin.ModelAdmin.raw_id_fields`
    * :attr:`~django.contrib.admin.ModelAdmin.readonly_fields`
    * A ``class Media`` to provide extra CSS and JavaScript files for the admin interface.

    The rendered output of a plugin is cached by default, assuming that most content is static.
    This also avoids extra database queries to retrieve the model objects.
    In case the plugin needs to output content dynamically, include ``cache_output = False`` in the plugin definition.
    """
    #: .. versionadded:: 1.1
    #:    Category for media
    MEDIA = _("Media")
    #: .. versionadded:: 1.1
    #:    Category for programming plugins
    PROGRAMMING = _("Programming")
    #: .. versionadded:: 1.1
    #:    Category for interactive plugins (e.g. forms, comments)
    INTERACTIVITY = _("Interactivity")
    #: .. versionadded:: 1.1
    #:    Category for advanced plugins (e.g. raw HTML, iframes)
    ADVANCED = _("Advanced")

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

    #: .. versionadded:: 0.9
    #: Cache the plugin output per :django:setting:`SITE_ID`.
    cache_output_per_site = False

    #: .. versionadded:: 1.0
    #: Cache the plugin output per language.
    #: This can be useful for sites which either:
    #:
    #: * Display fallback content on pages, but still use ``{% trans %}`` inside templates.
    #: * Dynamically switch the language per request, and *share* content between multiple languages.
    #:
    #: This option does not have to be used for translated CMS pages,
    #: as each page can have it's own set of :class:`~fluent_contents.models.ContentItem` objects.
    #: It's only needed for rendering the *same* item in different languages.
    cache_output_per_language = False

    #: .. versionadded: 1.0
    #: Set a custom cache timeout value
    cache_timeout = DEFAULT_TIMEOUT

    #: .. versionadded:: 1.0
    #: Tell which languages the plugin will cache.
    #: It defaults to the language codes from the :django:setting:`LANGUAGES` setting.
    cache_supported_language_codes = [code for code, _ in settings.LANGUAGES]

    #: The category title to place the plugin into.
    #: This is only used for the "Add Plugin" menu.
    #: You can provide a string here, :func:`~django.utils.translation.ugettext_lazy`
    #: or one of the predefined constants (:attr:`MEDIA`, :attr:`INTERACTIVITY:`, :attr:`PROGRAMMING` and :attr:`ADVANCED`).
    category = None

    #: .. versionadded:: 1.0
    #: By default, the plugin is rendered in the :attr:`language_code` it's written in.
    #: It can be disabled explicitly in case the content should be rendered language agnostic.
    #: For plugins that cache output per language, this will be done already.
    #:
    #: See also: :attr:`cache_output_per_language`
    render_ignore_item_language = False

    #: Alternative template for the view.
    ADMIN_TEMPLATE_WITHOUT_LABELS = "admin/fluent_contents/contentitem/admin_form_without_labels.html"

    #: .. versionadded:: 0.8.5
    #:    The ``HORIZONTAL`` constant for the :attr:`radio_fields`.
    HORIZONTAL = admin.HORIZONTAL

    #: .. versionadded:: 0.8.5
    #:    The ``VERTICAL`` constant for the :attr:`radio_fields`.
    VERTICAL = admin.VERTICAL

    #: The fields to display as raw ID
    raw_id_fields = ()

    #: The fields to display in a vertical filter
    filter_vertical = ()

    #: The fields to display in a horizontal filter
    filter_horizontal = ()

    #: The fields to display as radio choice. For example::
    #:
    #:    radio_fields = {
    #:        'align': ContentPlugin.VERTICAL,
    #:    }
    #:
    #: The value can be :attr:`ContentPlugin.HORIZONTAL` or :attr:`ContentPlugin.VERTICAL`.
    radio_fields = {}

    #: Fields to automatically populate with values
    prepopulated_fields = {}

    #: Overwritten formfield attributes, e.g. the 'widget'. Allows both the class and fieldname as key.
    formfield_overrides = {}

    #: The fields to display as readonly.
    readonly_fields = ()

    #: Define which fields could be used for indexing the plugin in a site (e.g. haystack)
    search_fields = []

    #: Define whether the full output should be used for indexing.
    search_output = None

    def __init__(self):
        self._type_id = None

    def __repr__(self):
        return '<{0} for {1} model>'.format(self.__class__.__name__, self.model.__name__)

    @property
    def verbose_name(self):
        """
        The title for the plugin, by default it reads the ``verbose_name`` of the model.
        """
        return self.model._meta.verbose_name

    @property
    def name(self):
        """
        Return the classname of the plugin, this is mainly provided for templates.
        This value can also be used in :func:`PluginPool`.
        """
        return self.__class__.__name__

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
                self._type_id = ContentType.objects.get_for_model(self.model, for_concrete_model=False).id
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
        result = self.render(request=request, instance=instance)

        if isinstance(result, ContentItemOutput):
            # Return in new 1.0 format

            # Also include the statically declared FrontendMedia, inserted before any extra added files.
            # These could be included already in the ContentItemOutput object, but duplicates are removed.
            media = self.get_frontend_media(instance)
            if media is not ImmutableMedia.empty_instance:
                result._insert_media(media)

            return result
        elif isinstance(result, (HttpResponseRedirect, HttpResponsePermanentRedirect)):
            # Can't return a HTTP response from a plugin that is rendered as a string in a template.
            # However, this response can be translated into our custom exception-based redirect mechanism.
            return self.redirect(result['Location'], result.status_code)
        else:
            # Old 0.9 syntax, wrap it.
            # The 'cacheable' is implied in the rendering already, but this is just for completeness.
            media = self.get_frontend_media(instance)
            return ContentItemOutput(result, media, cacheable=self.cache_output, cache_timeout=self.cache_timeout)

    def get_output_cache_base_key(self, placeholder_name, instance):
        """
        .. versionadded:: 1.0
           Return the default cache key, both :func:`get_output_cache_key` and :func:`get_output_cache_keys` rely on this.
           By default, this function generates the cache key using :func:`~fluent_contents.cache.get_rendering_cache_key`.
        """
        return get_rendering_cache_key(placeholder_name, instance)

    def get_output_cache_key(self, placeholder_name, instance):
        """
        .. versionadded:: 0.9
           Return the default cache key which is used to store a rendered item.
           By default, this function generates the cache key using :func:`get_output_cache_base_key`.
        """
        cachekey = self.get_output_cache_base_key(placeholder_name, instance)
        if self.cache_output_per_site:
            cachekey = "{0}-s{1}".format(cachekey, settings.SITE_ID)

        # Append language code
        if self.cache_output_per_language:
            # NOTE: Not using self.language_code, but using the current language instead.
            #       That is what the {% trans %} tags are rendered as after all.
            #       The render_placeholder() code can switch the language if needed.
            user_language = get_language()
            if user_language not in self.cache_supported_language_codes:
                user_language = 'unsupported'
            cachekey = "{0}.{1}".format(cachekey, user_language)

        return cachekey

    def get_output_cache_keys(self, placeholder_name, instance):
        """
        .. versionadded:: 0.9
           Return the possible cache keys for a rendered item.

           This method should be overwritten when implementing a function :func:`set_cached_output` method
           or when implementing a :func:`get_output_cache_key` function.
           By default, this function generates the cache key using :func:`get_output_cache_base_key`.
        """
        base_key = self.get_output_cache_base_key(placeholder_name, instance)
        cachekeys = [
            base_key,
        ]

        if self.cache_output_per_site:
            site_ids = list(Site.objects.values_list('pk', flat=True))
            if settings.SITE_ID not in site_ids:
                site_ids.append(settings.SITE_ID)

            base_key = get_rendering_cache_key(placeholder_name, instance)
            cachekeys = ["{0}-s{1}".format(base_key, site_id) for site_id in site_ids]

        if self.cache_output_per_language or self.render_ignore_item_language:
            # Append language code to all keys,
            # have to invalidate a lot more items in memcache.
            # Also added "None" suffix, since get_parent_language_code() may return that.
            # TODO: ideally for render_ignore_item_language, only invalidate all when the fallback language changed.
            total_list = []
            cache_languages = list(self.cache_supported_language_codes) + ['unsupported', 'None']

            # All variants of the Placeholder (for full page caching)
            placeholder = instance.placeholder
            total_list.extend(get_placeholder_cache_key(placeholder, lc) for lc in cache_languages)

            # All variants of the ContentItem in different languages
            for user_language in cache_languages:
                total_list.extend("{0}.{1}".format(base, user_language) for base in cachekeys)
            cachekeys = total_list

        return cachekeys

    def get_cached_output(self, placeholder_name, instance):
        """
        .. versionadded:: 0.9
           Return the cached output for a rendered item, or ``None`` if no output is cached.

           This method can be overwritten to implement custom caching mechanisms.
           By default, this function generates the cache key using :func:`get_output_cache_key`
           and retrieves the results from the configured Django cache backend (e.g. memcached).
        """
        cachekey = self.get_output_cache_key(placeholder_name, instance)
        return cache.get(cachekey)

    def set_cached_output(self, placeholder_name, instance, output):
        """
        .. versionadded:: 0.9
           Store the cached output for a rendered item.

           This method can be overwritten to implement custom caching mechanisms.
           By default, this function generates the cache key using :func:`~fluent_contents.cache.get_rendering_cache_key`
           and stores the results in the configured Django cache backend (e.g. memcached).

           When custom cache keys are used, also include those in :func:`get_output_cache_keys`
           so the cache will be cleared when needed.

        .. versionchanged:: 1.0
           The received data is no longer a HTML string, but :class:`~fluent_contents.models.ContentItemOutput` object.
        """
        cachekey = self.get_output_cache_key(placeholder_name, instance)
        if self.cache_timeout is not DEFAULT_TIMEOUT:
            cache.set(cachekey, output, self.cache_timeout)
        else:
            # Don't want to mix into the default 0/None issue.
            cache.set(cachekey, output)

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

        .. versionadded:: 1.0
           The function may either return a string of HTML code,
           or return a :class:`~fluent_contents.models.ContentItemOutput` object
           which holds both the CSS/JS includes and HTML string.
           For the sake of convenience and simplicity, most examples
           only return a HTML string directly.

           When the user needs to be redirected, simply return a :class:`~django.http.HttpResponseRedirect`
           or call the :func:`redirect` method.

        To render raw HTML code, use :func:`~django.utils.safestring.mark_safe` on the returned HTML.
        """
        render_template = self.get_render_template(request, instance, **kwargs)
        if not render_template:
            return str(_(u"{No rendering defined for class '%s'}" % self.__class__.__name__))

        context = self.get_context(request, instance, **kwargs)
        return self.render_to_string(request, render_template, context)

    def render_to_string(self, request, template, context, content_instance=None):
        """
        Render a custom template with the :class:`~PluginContext` as context instance.
        """
        if not content_instance:
            content_instance = PluginContext(request)

        content_instance.update(context)
        return render_to_string(template, content_instance.flatten())

    def render_error(self, error):
        """
        A default implementation to render an exception.
        """
        return '<div style="color: red; border: 1px solid red; padding: 5px;">' \
               '<p><strong>%s</strong></p>%s</div>' % (_('Error:'), linebreaks(escape(str(error))))

    def redirect(self, url, status=302):
        """
        .. versionadded:: 1.0
        Request a redirect to be performed for the user.
        Usage example:

        .. code-block:: python

            def get_context(self, request, instance, **kwargs):
                context = super(IdSearchPlugin, self).get_context(request, instance, **kwargs)

                if request.method == "POST":
                    form = MyForm(request.POST)
                    if form.is_valid():
                        self.redirect("/foo/")
                else:
                    form = MyForm()

                context['form'] = form
                return context

        To handle redirects, :class:`fluent_contents.middleware.HttpRedirectRequestMiddleware`
        should be added to the :django:setting:`MIDDLEWARE_CLASSES`.
        """
        raise HttpRedirectRequest(url, status=status)

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

    @property
    def frontend_media(self):
        """
        .. versionadded:: 1.0
        The frontend media, typically declared using a ``class FrontendMedia`` definition.
        """
        # By adding this property, frontend_media_property() is further optimized.
        return ImmutableMedia.empty_instance

    def get_frontend_media(self, instance):
        """
        Return the frontend media for a specific instance.
        By default, it returns ``self.frontend_media``, which derives
        from the ``class FrontendMedia`` of the plugin.
        """
        return self.frontend_media

    def get_search_text(self, instance):
        """
        Return a custom search text for a given instance.

        .. note:: This method is called when :attr:`search_fields` is set.
        """
        bits = get_search_field_values(instance)
        return clean_join(u" ", bits)


class HttpRedirectRequest(Exception):
    """
    .. versionadded:: 1.0
    Request for a redirect from within a view.
    """

    def __init__(self, url, status=302):
        super(HttpRedirectRequest, self).__init__(
            "A redirect to '{0}' was requested by a plugin.\n"
            "Please add 'fluent_contents.middleware.HttpRedirectRequestMiddleware' "
            "to MIDDLEWARE_CLASSES to handle redirects by plugins.".format(url)
        )
        self.url = url
        self.status = status
