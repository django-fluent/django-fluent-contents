.. _newplugins-rendering:

Customizing the frontend rendering
==================================

As displayed in the :doc:`models` page, a plugin is made of two classes:

* A model class in :file:`models.py`.
* A plugin class in :file:`content_plugins.py`.

The plugin class renders the model instance using:

* A custom :func:`~fluent_contents.extensions.ContentPlugin.render` method.

* The :attr:`~fluent_contents.extensions.ContentPlugin.render_template` attribute,
  :func:`~fluent_contents.extensions.ContentPlugin.get_render_template` method
  and optionally :func:`~fluent_contents.extensions.ContentPlugin.get_context` method.

Simply stated, a plugin provides the "view" of a "model".


Simple rendering
----------------

To quickly create plugins with little to no effort, only the :attr:`~fluent_contents.extensions.ContentPlugin.render_template` needs to be specified.
The template code receives the model object via the ``instance`` variable.

To switch the template depending on the model, the :func:`~fluent_contents.extensions.ContentPlugin.get_render_template` method
can be overwritten instead. For example:

.. code-block:: python

    @plugin_pool.register
    class MyPlugin(ContentPlugin):
        # ...

        def get_render_template(self, request, instance, **kwargs):
            return instance.template_name or self.render_template


To add more context data, overwrite the :class:`~fluent_contents.extensions.ContentPlugin.get_context` method.
The :ref:`twitterfeed <twitterfeed>` plugins use this for example to pass settings to the template:

.. code-block:: python

    @plugin_pool.register
    class MyPlugin(ContentPlugin):
        # ...

        def get_context(self, request, instance, **kwargs):
            context = super(MyPlugin, self).get_context(request, instance, **kwargs)
            context.update({
                'AVATAR_SIZE': int(appsettings.FLUENT_TWITTERFEED_AVATAR_SIZE),
                'REFRESH_INTERVAL': int(appsettings.FLUENT_TWITTERFEED_REFRESH_INTERVAL),
                'TEXT_TEMPLATE': appsettings.FLUENT_TWITTERFEED_TEXT_TEMPLATE,
            })
            return context

For most scenario's, this provides simple flexibility with a DRY approach.


Custom rendering
----------------

Instead of only providing extra context data,
the whole :func:`~fluent_contents.extensions.ContentPlugin.render` method can be overwritten as well.

It should return a string with the desired output.
For example, this is the render function of the :ref:`text <text>` plugin:

.. code-block:: python

    def render(self, request, instance, **kwargs):
        return mark_safe('<div class="text">' + instance.text + '</div>\n')

The standard :func:`~fluent_contents.extensions.ContentPlugin.render` method basically does the following:

.. code-block:: python

    def render(self, request, instance, **kwargs):
        template = self.get_render_template(request, instance, **kwargs)
        context = self.get_context(request, instance, **kwargs)
        return self.render_to_string(request, template, context)

* It takes the template from :func:`~fluent_contents.extensions.ContentPlugin.get_render_template`.
* It uses the the context provided by :func:`~fluent_contents.extensions.ContentPlugin.get_context`.
* It uses :func:`~fluent_contents.extensions.ContentPlugin.render_to_string` method which adds the ``STATIC_URL`` and ``MEDIA_URL`` variables in the template.

The output will be escaped by default, so use Django's :func:`~django.utils.html.format_html`
or :func:`~django.utils.safestring.mark_safe` when content should not be escaped.
Hence, it's preferred to use a template unless that makes things more complex.

Internally, the :func:`~fluent_contents.extensions.ContentPlugin.render_to_string` method
wraps the rendering context in a :func:`~fluent_contents.extensions.PluginContext`.
which is similar to the :class:`~django.template.RequestContext` that Django provides.


Form processing
---------------

An entire form with GET/POST can be handled with a plugin.
This happens again by overwriting :func:`~fluent_contents.extensions.ContentPlugin.render` method.

For example, a "Call me back" plugin can be created using a
custom :func:`~fluent_contents.extensions.ContentPlugin.render` function:

.. code-block:: python

    @plugin_pool.register
    class CallMeBackPlugin(ContentPlugin):
        model = CallMeBackItem
        category = _("Contact page")
        render_template = "contentplugins/callmeback/callmeback.html"
        cache_output = False   # Important! See "Output caching" below.

        def render(self, request, instance, **kwargs):
            context = self.get_context(request, instance, **kwargs)
            context['completed'] = False

            if request.method == 'POST':
                form = CallMeBackForm(request.POST, request.FILES)
                if form.is_valid():
                    instance = form.save()
                    return self.redirect(reverse('thank-you-page'))
            else:
                form = CallMeBackForm()

            context['form'] = form
            return self.render_to_string(request, self.render_template, context)

.. note::

    The :attr:`~fluent_contents.extensions.ContentPlugin.cache_output` attribute is ``False``
    to disable the default output caching. The POST screen would return the cached output instead.

To allow plugins to perform directs,
add :class:`fluent_contents.middleware.HttpRedirectRequestMiddleware`
to :django:setting:`MIDDLEWARE_CLASSES`.


Frontend media
--------------

Plugins can specify additional JS/CSS files which should be included.
For example:

.. code-block:: python

    @plugin_pool.register
    class MyPlugin(ContentPlugin):
        # ...

        class FrontendMedia:
            css = {
                'all': ('myplugin/all.css',)
            }
            js = (
                'myplugin/main.js',
            )

Equally, there is a :attr:`~fluent_contents.extensions.ContentPlugin.frontend_media` property,
and :attr:`~fluent_contents.extensions.ContentPlugin.get_frontend_media` method.

.. _output-caching:

Output caching
--------------

By default, plugin output is cached and only refreshes when the administrator saves the page.
This greatly improves the performance of the web site, as very little database queries are needed,
and most pages look the same for every visitor anyways.

* When the plugin output is dynamic set the :attr:`~fluent_contents.extensions.ContentPlugin.cache_output` to ``False``.
* When the plugin output differs per :django:setting:`SITE_ID` only,
  set :attr:`~fluent_contents.extensions.ContentPlugin.cache_output_per_site` to ``True``.
* When the plugin output differs per language,
  set :attr:`~fluent_contents.extensions.ContentPlugin.cache_output_per_language` to ``True``.
* When the output should be refreshed more often,
  change the :attr:`~fluent_contents.extensions.ContentPlugin.cache_timeout`.
* As last resort, the caching can be disabled entirely project-wide using the :ref:`FLUENT_CONTENTS_CACHE_OUTPUT` setting.
  This should be used temporary for development, or special circumstances only.

Most plugins deliver exactly the same content for every request, hence the setting is tuned for speed by default.
Further more, this lets plugin authors make a conscious decision about caching, and to avoid unexpected results in production.

When a plugin does a lot of processing at render time
(e.g. requesting a web service, parsing text, sanitizing HTML, or do XSL transformations of content),
consider storing the intermediate rendering results in the database using the :func:`~django.db.models.Model.save` method of the model.
The :ref:`code plugin <code>` uses this for example to store the highlighted code syntax.
The :func:`~fluent_contents.extensions.ContentPlugin.render` method can just read the value.


Development tips
~~~~~~~~~~~~~~~~

In :django:setting:`DEBUG` mode, changes to the :attr:`~fluent_contents.extensions.ContentPlugin.render_template`
are detected, so this doesn't affect the caching. Some changes however, will not be detected (e.g. include files).
A quick way to clear memcache, is by using nc/ncat/netcat::

    echo flush_all | nc localhost 11211

When needed, include ``FLUENT_CONTENTS_CACHE_OUTPUT = False`` in the settings file.
