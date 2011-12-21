.. _formdesignerlink:

The formdesignerlink plugin
===========================

The `formdesignerlink` plugin displays a form, created by
the `django-formdesigner <https://github.com/philomat/django-form-designer>`_ module.

.. note::
    While the `formdesigner` interface may not be fully up to the "UI standards" of `django-fluent-contents`,
    it is however a popular module, and hence this plugin is provided!

Installation
------------

Add the following settings to ``settings.py``:

.. code-block:: python

    INSTALLED_APPS += (
        'form_designer',
        'fluent_contents.plugins.formdesignerlink',
    )

Each page can now be enriched with a form, that was created by the `formdesigner` application.

Configuration
-------------

To customize the output, configure the ``django-form-designer`` application via the settings file.
Some relevant settings are:

``FORM_DESIGNER_DEFAULT_FORM_TEMPLATE``
    Defines the default template to use to render a form.
    For example, the template can be rendered with ``django-uni-form``.

``FORM_DESIGNER_FORM_TEMPLATES``
    Defines a list of choices, to allow users to select a template.

``FORM_DESIGNER_FIELD_CLASSES``
    A list of choices, to define which Django field types are allowed.

``FORM_DESIGNER_WIDGET_CLASSES``
    A list of choices, to define which Django widget types are allowed.

Further information can be found in the source code of `django-formdesigner`.
(`e.g. settings.py <https://github.com/philomat/django-form-designer/blob/master/form_designer/settings.py>`_).

