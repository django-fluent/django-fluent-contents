.. _picture:

The picture plugin
==================

.. versionadded:: 0.9.0
   The `picture` plugin provides a simple structured way to add images to the page content.

..

  .. image:: /images/plugins/picture-admin.*
     :width: 733px
     :height: 349px

Pictures are outputted in a ``<figure>`` element and can optionally have a ``<figcaption>``:

  .. image:: /images/plugins/picture-html.*
     :width: 514px
     :height: 270px


Installation
------------

Add the following settings to ``settings.py``:

.. code-block:: python

    INSTALLED_APPS += (
        'fluent_contents.plugins.picture',
    )

The plugin does not provide additional configuration options.


Using improved models fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, the standard Django :class:`~django.db.models.ImageField` and :class:`~django.db.models.URLField` are used.
By including django-any-imagefield_ and django-any-urlfield_ in the project, this application will use those fields instead.
See the :ref:`optional integration with other packages <optional-integration>` chapter to enable these features.


Configuration
-------------

The following settings are available:

.. code-block:: python

    FLUENT_PICTURE_UPLOAD_TO = '.'


FLUENT_PICTURE_UPLOAD_TO
~~~~~~~~~~~~~~~~~~~~~~~~

The upload folder for all pictures. Defaults to the root of the media folder.



.. _django-any-imagefield:  https://github.com/edoburu/django-any-imagefield
.. _django-any-urlfield: https://github.com/edoburu/django-any-urlfield
.. _django-filebrowser: https://github.com/smacker/django-filebrowser-no-grappelli-django14
