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
The default editor is the YUI editor, because it works out of the box.
Other editors, like the CKEditor_, Redactor_ and TinyMCE_ are supported
with some additional configuration.
See the django-wysiwyg_ documentation for details

.. important::

    There is no reason to feel constrained to a specific editor.
    Firstly, the editor can be configured by configuring django-wysiwyg_.
    Secondly, it's possible to create a different text plugin yourself,
    and let this plugin serve as canonical example.


Installation
------------

Install the dependencies via *pip*::

    pip install django-fluent-contents[text]

This installs the django-wysiwyg_ package.

Add the following settings to ``settings.py``:

.. code-block:: python

    INSTALLED_APPS += (
        'fluent_contents.plugins.text',
        'django_wysiwyg',
    )


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
As of django-wysiwyg_ 0.5.1, the following editors are available:

* **ckeditor** - The CKEditor_, formally known as FCKEditor.
* **redactor** - The Redactor_ editor (requires a license).
* **tinymce** - The TinyMCE_ editor, in simple mode.
* **tinymce_advanced** - The TinyMCE_ editor with many more toolbar buttons.
* **yui** - The YAHOO_ editor (the default)
* **yui_advanced** - The YAHOO_ editor with more toolbar buttons.

Additional editors can be easily added, as the setting refers to a set of templates names:

* django_wysiwyg/**flavor**/includes.html
* django_wysiwyg/**flavor**/editor_instance.html

For more information, see the documentation of django-wysiwyg_
about `extending django-wysiwyg <http://django-wysiwyg.readthedocs.org/en/latest/extending.html>`_.


FLUENT_TEXT_CLEAN_HTML
~~~~~~~~~~~~~~~~~~~~~~

If ``True``, the HTML tags will be rewritten to be well-formed.
This happens using either one of the following packages:

* html5lib_
* pytidylib_


FLUENT_TEXT_SANITIZE_HTML
~~~~~~~~~~~~~~~~~~~~~~~~~

if ``True``, unwanted HTML tags will be removed server side using html5lib_.

.. _CKEditor: http://ckeditor.com/
.. _Redactor: http://redactorjs.com/
.. _TinyMCE: http://www.tinymce.com/
.. _YAHOO: http://developer.yahoo.com/yui/editor/
.. _django-ckeditor: https://github.com/shaunsephton/django-ckeditor
.. _django-tinymce: https://github.com/aljosa/django-tinymce
.. _django-wysiwyg: https://github.com/pydanny/django-wysiwyg
.. _html5lib: http://code.google.com/p/html5lib/
.. _pytidylib: http://countergram.com/open-source/pytidylib

