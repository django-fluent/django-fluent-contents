.. _optional-integration:

Optional integration with other packages
========================================

.. versionadded:: 0.9.0

By default, this package works without including other packages in ``INSTALLED_APPS``.
There is no requirement to use a specific file manager or WYSIWYG editor in your project.
However, the features of this package can be enhanced by installing a few additional applications.


Custom URL fields
-----------------

By installing django-any-urlfield_, the URL fields can select both internal and external URLs:

.. figure:: /images/fields/anyurlfield1.*
   :width: 363px
   :height: 74px
   :alt: AnyUrlField, with external URL input.

.. figure:: /images/fields/anyurlfield2.*
   :width: 290px
   :height: 76px
   :alt: AnyUrlField, with internal page input.

The :ref:`picture plugin <picture>` and :class:`~fluent_contents.extensions.PluginUrlField` class
use this to display the URL field.

Install it via::

    pip install django-any-urlfield

And include it in the settings:

.. code-block:: python

    INSTALLED_APPS += (
        'any_urlfield',
        'any_imagefield',
    )

Each model which provides a ``get_absolute_url`` field can be used as form option.

For more information, see the documentation of django-any-urlfield_.


Custom file and image fields
----------------------------

By installing django-any-imagefield_, file and image fields can be replaced with a file browser:

.. figure:: /images/fields/filebrowsefield.*
   :width: 300px
   :height: 100px
   :alt: AnyImageField, with django-filebrowser.

The :ref:`picture plugin <picture>`, :class:`~fluent_contents.extensions.PluginFileField`
and :class:`~fluent_contents.extensions.PluginImageField` class use this to display the file field.

Install it via::

    pip install django-any-imagefield
    pip install -e git+git://github.com/smacker/django-filebrowser-no-grappelli-django14.git#egg=django-filebrowser

And include it in the settings:

.. code-block:: python

    INSTALLED_APPS += (
        'any_imagefield',
        'filebrowser',
    )

And update ``urls.py``:

.. code-block:: python

    from filebrowser.sites import site as fb_site

    urlpatterns += [
        url(r'^admin/filebrowser/', include(fb_site.urls)),
    ]


This package either uses the standard Django :class:`~django.db.models.ImageField`,
or the image field from any other supported application.
When sorl-thumbnail_ is installed, it will be used; when django-filebrowser-no-grappelli-django14_ is available it's used instead.

For more information, see the documentation of django-any-imagefield_.


Custom HTML / WYSIWYG fields
----------------------------

The :ref:`text plugin <text>` and :class:`~fluent_contents.extensions.PluginHtmlField`
use django-wysiwyg_ to display a WYSIWYG editor.

It's possible to switch to any WYSIWYG editor of your choice.
The default editor is the YUI editor, because it works out of the box.
Other editors, like the CKEditor_, Redactor_ and TinyMCE_ are supported
with some additional configuration.

For more information, see the documentation of django-wysiwyg_.


Debug toolbar
-------------

During development, the rendered items can be displayed in a special django-debug-toolbar_ panel.
Include ``'fluent_contents.panels.ContentPluginPanel'`` in the ``DEBUG_TOOLBAR_PANELS`` setting.


.. _CKEditor: http://ckeditor.com/
.. _Redactor: http://redactorjs.com/
.. _TinyMCE: http://www.tinymce.com/
.. _YAHOO: http://developer.yahoo.com/yui/editor/
.. _django-any-urlfield: https://github.com/edoburu/django-any-urlfield
.. _django-any-imagefield: https://github.com/edoburu/django-any-imagefield
.. _django-debug-toolbar: https://github.com/django-debug-toolbar/django-debug-toolbar
.. _django-filebrowser-no-grappelli-django14: https://github.com/smacker/django-filebrowser-no-grappelli-django14
.. _django-wysiwyg: https://github.com/pydanny/django-wysiwyg
.. _sorl-thumbnail: https://github.com/sorl/sorl-thumbnail
