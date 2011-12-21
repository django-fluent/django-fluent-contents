.. _googledocsviewer:

The googledocsviewer plugin
===========================

The `googledocsviewer` plugin allows inserting an embedded Google Docs Viewer in the page.
This can be used to display various files - like PDF or DOCX files - inline in the HTML page.

Installation
------------

Add the following settings to ``settings.py``:

.. code-block:: python

    INSTALLED_APPS += (
        'fluent_contents.plugins.googledocsviewer',
    )

The plugin does not provide additional configuration options, nor does it have dependencies on other packages.

.. note::

    When using the Google Docs viewer on your site,
    Google assumes you agree with the Terms of Service, see: https://docs.google.com/viewer/TOS
