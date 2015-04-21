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

The plugin does not have dependencies on other packages.


Configuration
-------------

No settings have to be defined.
For further tuning however, the following settings are available:

.. code-block:: python

    FLUENT_SHARED_CONTENT_ENABLE_CROSS_SITE = False


.. _FLUENT_SHARED_CONTENT_ENABLE_CROSS_SITE:

FLUENT_SHARED_CONTENT_ENABLE_CROSS_SITE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, each :class:`~django.contrib.sites.models.Site` model has it's own contents.
Each site has it's own set of shared contents objects.

By enabling this flag, the admin interface provides a "Share between all sites" setting.
This can be found in the collapsed "Publication settings" tab.
Once enabled, a shared content item is visible across all websites that the Django instance hosts.

This can be enabled to support content such as the text of an "About" or  "Terms and Conditions" page.

When :ref:`FLUENT_CONTENTS_FILTER_SITE_ID` is disabled, this feature is nullified,
as all contents is always available across all sites.


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

.. note::
   When a template is used, the system assumes that the output can change per request.
   Hence, the output of individual items will be cached, but the final merged output is no longer cached.
   Add ``cachable=1`` to enable output caching for templates too.
