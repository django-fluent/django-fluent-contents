.. _oembeditem:

The oembeditem plugin
===========================

The `oembeditem` plugin allows inserting an embedded online content in the page,
such as a YouTube video, Slideshare presentation or Flickr photo.

  .. image:: /images/plugins/oembeditem-admin.*
     :width: 957px
     :height: 166px

The presentation is rendered with the embed code:

  .. image:: /images/plugins/oembeditem-html.*
     :width: 430px
     :height: 384px


Installation
------------

Add the following settings to ``settings.py``:

.. code-block:: python

    INSTALLED_APPS += (
        'fluent_contents.plugins.oembeditem',
    )

The dependencies can be installed via `pip`::

    pip install micawber

The plugin does not provide additional configuration options.
