.. _templatetags:

The template tags
=================

The template tags provide the rendering of placeholder content.
Load the tags using:

.. code-block:: html+django

    {% load placeholder_tags %}

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

The metadata can be extracted with the :class:`~fluent_contents.templatetags.placeholder_tags.PagePlaceholderNode` class,
and :mod:`fluent_contents.analyzer` module.
