.. _sharedcontent:

The sharedcontent plugin
========================

.. versionadded:: 0.8.5
   The `sharedcontent` plugin allows inserting an content at multiple locations in the site.

..

  .. image:: /images/plugins/sharedcontent-admin1.*
     :width: 770px
     :height: 422px

The shared content can be included in the site:

  .. image:: /images/plugins/sharedcontent-admin2.*
     :width: 733px
     :height: 65px


Installation
------------

Add the following settings to ``settings.py``:

.. code-block:: python

    INSTALLED_APPS += (
        'fluent_contents.plugins.sharedcontent',
    )

The plugin does not provide additional configuration options, nor does it have dependencies on other packages.


Usage in templates
------------------

To hard-code the shared content in a template, use:

.. code-block:: html+django

    {% load sharedcontent_tags %}

    {% sharedcontent "template-code-name" %}

To customize the placeholder contents, a template can be specified:

.. code-block:: html+django

    {% sharedcontent "template-code-name" template="mysite/parts/slot_placeholder.html" %}

That template should loop over the content items, and include additional HTML.
For example:

.. code-block:: html+django

    {% for contentitem, html in contentitems %}
      {% if not forloop.first %}<div class="splitter"></div>{% endif %}
      {{ html }}
    {% endfor %}
