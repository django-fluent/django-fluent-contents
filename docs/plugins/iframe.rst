.. _iframe:

The iframe plugin
=================

The `iframe` plugin allows inserting IFrames to the page.

  .. image:: /images/plugins/iframe-admin.*
     :width: 732px
     :height: 186px

The frame is displayed at the website:

  .. image:: /images/plugins/iframe-html.*
     :width: 552px
     :height: 202px

Generally, such feature is useful for large web sites where a specific service or contact form needs to be embedded.
In case a variation is needed, this plugin can easily be used as starting point for writing a custom plugin.


Installation
------------

Add the following settings to ``settings.py``:

.. code-block:: python

    INSTALLED_APPS += (
        'fluent_contents.plugins.iframe',
    )

The plugin does not provide additional configuration options, nor does it have dependencies on other packages.

The appearance of the ``<iframe>`` tag depends on the CSS style of the web site.
Generally, at least a ``border`` should be defined.
