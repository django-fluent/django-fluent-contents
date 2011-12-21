.. _rawhtml:

The rawhtml plugin
==================

The `rawhtml` plugin allows inserting raw HTML code in the page.
This can be used for example for:

* including `jQuery <http://jquery.org/>`_ snippets in a page.
* including "embed codes" in a page, provided by sites such as Facebook, Google Docs, YouTube, SlideShare, and Vimeo.

Installation
------------

Add the following settings to ``settings.py``:

.. code-block:: python

    INSTALLED_APPS += (
        'fluent_contents.plugins.rawhtml',
    )

The plugin does not provide additional configuration options, nor does it have dependencies on other packages.
