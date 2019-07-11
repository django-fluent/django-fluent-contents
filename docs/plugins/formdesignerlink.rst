.. _formdesignerlink:

The formdesignerlink plugin
===========================

The `formdesignerlink` plugin displays a form, created by the django-form-designer-ai_ module.

  .. image:: /images/plugins/formdesignerlink-admin.*
     :width: 732px
     :height: 65px

The form is displayed at the website:

  .. image:: /images/plugins/formdesignerlink-html.*
     :width: 470px
     :height: 405px

.. note::
    While the `form_designer` interface may not be fully up to the "UI standards" of `django-fluent-contents`,
    it is however a popular module, and hence this plugin is provided!


Installation
------------

Install the dependencies via *pip*::

    pip install django-fluent-contents[formdesignerlink]

This installs django-form-designer-ai_.

Add the following settings to ``settings.py``:

.. code-block:: python

    INSTALLED_APPS += (
        'form_designer',
        'fluent_contents.plugins.formdesignerlink',
    )

To display previews, the `form_designer` application also requires an additional line in ``urls.py``:

.. code-block:: python

    urlpatterns += [
        url(r'^forms/', include('form_designer.urls')),
    ]

Each page can now be enriched with a form, that was created by the `form_designer` application.


Configuration
-------------

To customize the output, configure the ``django-form-designer-ai`` application via the settings file.
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

It is also highly recommended to overwrite the ``form_designer/templates/html/formdefinition/base.html`` template,
which is used to provide previews for the form in the admin interface.

Further information can be found in the source code of `django-formdesigner`.
(`e.g. settings.py <https://github.com/andersinno/django-form-designer-ai/blob/master/form_designer/settings.py>`_).

.. _django-form-designer-ai: https://github.com/andersinno/django-form-designer-ai
