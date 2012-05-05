.. _text:

The text plugin
===============

The `text` plugin provides a standard WYSIWYG ("What You See is What You Get")
editor in the administration panel, to add HTML contents to the page.

.. image:: /images/plugins/text-admin.*
   :width: 732px
   :height: 269px

.. not needed: image:: /images/plugins/text-html.*
   :width: 398px
   :height: 52px

The plugin is built on top of django-wysiwyg_, making it possible
to switch to any WYSIWYG editor of your choice.

Installation
------------

Add the following settings to ``settings.py``:

.. code-block:: python

    INSTALLED_APPS += (
        'fluent_contents.plugins.text',
        'django_wysiwyg',
    )

The dependencies can be installed via `pip`::

    pip install django-wysiwyg

Configuration
-------------

The following settings are available:

.. code-block:: python

    DJANGO_WYSIWYG_FLAVOR = "yui_advanced"

    FLUENT_TEXT_CLEAN_HTML = True
    FLUENT_TEXT_SANITIZE_HTML = True


DJANGO_WYSIWYG_FLAVOR
~~~~~~~~~~~~~~~~~~~~~

The ``DJANGO_WYSIWYG_FLAVOR`` setting defines which WYSIWYG editor will be used.
As of django-wysiwyg 0.3, the following editors are available:

* **ckeditor**: The CKEditor, formally known as FCKEditor
* **yui**: The YAHOO editor.
* **yui_advanced**: The YAHOO editor with more toolbar buttons.

Additional editors can be easily added, as the setting refers to a set of templates names:

* django_wysiwyg/**flavor**/includes.html
* django_wysiwyg/**flavor**/editor_instance.html

For more information, see the documentation of django-wysiwyg_
about `extending django-wysiwyg <http://django-wysiwyg.readthedocs.org/en/latest/extending.html>`_.


FLUENT_TEXT_CLEAN_HTML
~~~~~~~~~~~~~~~~~~~~~~

If ``True``, bad HTML tags will be cleaned up server side using either one of the following modules:

* ``html5lib``
* ``pytidylib``

FLUENT_TEXT_SANITIZE_HTML
~~~~~~~~~~~~~~~~~~~~~~~~~

if ``True``, the HTML insecure items will be removed server side using ``html5lib``.

.. _django-wysiwyg: https://github.com/pydanny/django-wysiwyg
