.. _rawhtml:

The rawhtml plugin
==================

The `rawhtml` plugin allows inserting raw HTML code in the page.

  .. image:: /images/plugins/rawhtml-admin2.*
     :width: 732px
     :height: 122px

The code is included as-is at the frontend:

  .. image:: /images/plugins/rawhtml-html2.*
     :width: 420px
     :height: 315px


This plugin can be used for example for:

* including "embed codes" in a page, provided by sites such as Facebook, Google Docs, YouTube, SlideShare, and Vimeo.
* including `jQuery <http://jquery.org/>`_ snippets in a page:

  .. image:: /images/plugins/rawhtml-admin.*
     :width: 732px
     :height: 212px

Installation
------------

Add the following settings to ``settings.py``:

.. code-block:: python

    INSTALLED_APPS += (
        'fluent_contents.plugins.rawhtml',
    )

The plugin does not provide additional configuration options, nor does it have dependencies on other packages.
