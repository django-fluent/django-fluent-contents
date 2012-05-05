.. _googledocsviewer:

The googledocsviewer plugin
===========================

The `googledocsviewer` plugin allows inserting an embedded Google Docs Viewer in the page.
This can be used to display various files - like PDF or DOCX files - inline in the HTML page.

  .. image:: /images/plugins/googledocsviewer-admin.*
     :width: 732px
     :height: 208px

The document is rendered by Google:

  .. image:: /images/plugins/googledocsviewer-html.*
     :width: 552px
     :height: 602px


Installation
------------

Add the following settings to ``settings.py``:

.. code-block:: python

    INSTALLED_APPS += (
        'fluent_contents.plugins.googledocsviewer',
    )

The plugin does not provide additional configuration options, nor does it have dependencies on other packages.

The Google Docs Viewer is rendered as ``<iframe>`` tag.
The appearance of the ``<iframe>`` tag depends on the CSS style of the web site.
Generally, at least a ``border`` should be defined.


.. note::

    When using the Google Docs viewer on your site,
    Google assumes you agree with the Terms of Service, see: https://docs.google.com/viewer/TOS
