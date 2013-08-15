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

Extra meta information can be provided for the admin interface:

.. code-block:: html+django

    {% page_placeholder currentpage "slotname" title="Tab title" role="main %}

The metadata can be extracted with the :class:`~fluent_contents.templatetags.fluent_contents_tags.PagePlaceholderNode` class,
and :mod:`fluent_contents.analyzer` module.


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

This way, the contents can be minified too, using django-compressor_ for example.


Note for existing projects
--------------------------

.. deprecated:: 1.0
   Previously, the template tag library was called *placeholder_tags*.
   Using the old style import still works. It's recommended to change it:

.. code-block:: html+django

    {% load placeholder_tags %}


.. _django-compressor: https://github.com/jezdez/django_compressor
