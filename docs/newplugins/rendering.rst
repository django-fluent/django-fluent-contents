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

.. warning::

    When implementing a custom :func:`~fluent_contents.extensions.ContentPlugin.render` method, you need to take care of output escaping as well.
    Unless the content is meant to be used as HTML, the variables should be escaped with the :func:`django.utils.html.escape` function.
    Hence, it's preferred to use a template unless it's either too much hassle, or the workflow is too complex.

Internally, the :func:`~fluent_contents.extensions.ContentPlugin.render_to_string` method
wraps the rendering context in a :func:`~fluent_contents.extensions.PluginContext`.
which is similar to the :class:`~django.template.RequestContext` that Django provides.


Complex workflows
-----------------

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
        cache_output = False

        def render(self, request, instance, **kwargs):
            context = self.get_context(request, instance, **kwargs)
            context['completed'] = False

            if request.method == 'POST':
                form = CallMeBackForm(request.POST, request.FILES)
                if form.is_valid():
                    instance = form.save()
                    context['completed'] = True
                    # TODO: request to redirect the page, currently it just leaves the page in the post state.
            else:
                form = CallMeBackForm()

            context['form'] = form
            return self.render_to_string(request, self.render_template, context)

.. note::

    The :attr:`~fluent_contents.extensions.ContentPlugin.cache_output` attribute is ``False``
    to disable the default output caching. The POST screen would return the cached output instead.


Output caching
--------------

By default, plugin output is cached and only refreshes when the administrator saves the page.
This greatly improves the performance of the web site, as very little database queries are needed,
and most pages look the same for every visitor anyways.

When the plugin output differs per user or request however, set
the :attr:`~fluent_contents.extensions.ContentPlugin.cache_output` to ``False``.

The attribute is ``True`` by default, to let plugin authors make a conscious decision about caching.
Most plugins deliver exactly the same content for every request, hence the setting is tuned for speed by default.

For special circumstances, the caching can be disabled entirely project-wide using the :ref:`FLUENT_CONTENTS_CACHE_OUTPUT` setting.

In case a rendering needs to do a lot of processing
(e.g. requesting a web service, parsing text, sanitizing HTML, or do XSL tramsformations of content),
also consider to store an intermediate result at the :func:`~django.db.models.Model.save` method of the model.
The :func:`~fluent_contents.extensions.ContentPlugin.render` method can just read the value.
