.. _templatetags:

The template tags
=================

The template tags provide the rendering of placeholder content.
Load the tags using:

.. code-block:: html+django

    {% load fluent_contents_tags %}

To render a placeholder for a given object, use:

.. code-block:: html+django

    {% render_placeholder myobject.placeholder_field %}

CMS Page placeholders
---------------------

To define the placeholders for a :doc:`cms <cms>` page, use:

.. code-block:: html+django

    {% page_placeholder currentpage "slotname" %}

If the currentpage variable is named ``page``, it can be left out.

Using a custom template
~~~~~~~~~~~~~~~~~~~~~~~

To customize the placeholder contents, a template can be specified:

.. code-block:: html+django

    {% page_placeholder currentpage "slotname" template="mysite/parts/slot_placeholder.html" %}

That template should loop over the content items, and include additional HTML.
For example:

.. code-block:: html+django

    {% for contentitem, html in contentitems %}
      {% if not forloop.first %}<div class="splitter"></div>{% endif %}
      {{ html }}
    {% endfor %}

The following variables are available:

* ``contentitems`` - a list with:

 * the :class:`~fluent_contents.models.ContentItem` model.
   You can access ``contentitem.plugin.name`` to read the actual plugin name.
   The model itself is generally not downcasted to the actual model.
 * the rendered HTML code

* ``parent_object`` - the parent object, this may be ``None`` if :func:`~fluent_contents.rendering.render_items`
  was used instead of :func:`~fluent_contents.rendering.render_placeholder`.

.. note::
   When a template is used, the system assumes that the output can change per request.
   Hence, even though :ref:`FLUENT_CONTENTS_CACHE_PLACEHOLDER_OUTPUT` may be set,
   but the final merged output will no longer be cached.
   Add ``cachable=1`` to enable output caching for templates too.

   The output of individual items will always be cached,
   as that is subject to the :ref:`FLUENT_CONTENTS_CACHE_OUTPUT` setting.

Admin Meta information
~~~~~~~~~~~~~~~~~~~~~~

Extra meta information can be provided for the admin interface:

.. code-block:: html+django

    {% page_placeholder currentpage "slotname" title="Tab title" role="main %}

The metadata can be extracted with the :class:`~fluent_contents.templatetags.fluent_contents_tags.PagePlaceholderNode` class,
and :mod:`fluent_contents.analyzer` module.

Fallback languages
~~~~~~~~~~~~~~~~~~

.. versionadded:: 1.0
   For multilingual sites, the contents of the active translation will be displayed only.
   To render the fallback language for empty placeholders, use the ``fallback`` parameter:

   .. code-block:: html+django

       {% page_placeholder currentpage "slotname" fallback=1 %}

   This can be used to display the "english" content everywhere by default for example,
   until a translator fills the contents of the page.
   The fallback language is defined in the :ref:`FLUENT_CONTENTS_DEFAULT_LANGUAGE_CODE` setting.


Frontend media
--------------

To render the CSS/JS includes of content items, use:

.. code-block:: html+django

    {% render_content_items_media %}

This tag should be placed at the bottom of the page, after all plugins are rendered.

Optionally, specify to render only the CSS or JavaScript content:

.. code-block:: html+django

    {% render_content_items_media css %}
    {% render_content_items_media js %}
    {% render_content_items_media js internal %}
    {% render_content_items_media js external %}

By adding the ``local`` or ``external`` flag, the media files will be split into:

* externally hosted files which should *not* be compressed (e.g. a plugin that includes the Google Maps API).
* locally hosted files which can be compressed.

This way, the contents can be minified too, using django-compressor_ for example:

.. code-block:: html+django

    {% load compress fluent_contents_tags %}

    {% render_content_items_media css external %}
    {% compress css %}
        {% render_content_items_media css internal %}
    {% endcompress %}

    {% render_content_items_media js external %}
    {% compress js %}
        {% render_content_items_media js local %}
        {% block extra_scripts %}{% endblock %}
    {% endcompress %}


Note for existing projects
--------------------------

.. deprecated:: 1.0
   Previously, the template tag library was called *placeholder_tags*.
   Using the old style import still works. It's recommended to change it:

.. code-block:: html+django

    {% load placeholder_tags %}


.. _django-compressor: https://github.com/jezdez/django_compressor
