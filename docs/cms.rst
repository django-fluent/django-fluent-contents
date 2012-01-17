.. _cms:

Creating a CMS system
=====================

Besides the :class:`~fluent_contents.models.PlaceholderField` class,
thee `fluent_contents` module also provides additional admin classes to build a CMS interface.
This can be used

The main difference between the CMS interface, and :class:`~fluent_contents.models.PlaceholderField`
class is that the placeholders will be created dynamically based on the template of the current page.
Instead of displaying placeholders inline in the form, the placeholder content is displayed
in a separate tabbar interface.

The features include:

* Detecting placeholders from a Django template.
* Automaticaly rearrange content items when the layout changes.
* Allow usage with any parent model.

In the source distribution, see the ``example.simple`` package for a working demonstration.

.. seealso::

    The API documentation of the :ref:`fluent_contents.admin` module provides more details of the classes.

The basic setup
---------------

The start of the admin interface, is the current interface for the CMS `Page` object.
To display the "placeholder editor", the admin screen needs to inherit
from :class:`~fluent_contents.admin.PlaceholderEditorAdmin`,
and implement the :func:`~fluent_contents.admin.PlaceholderEditorAdmin.get_placeholder_data` method.

.. code-block:: python

    from django.contrib import admin
    from fluent_contents.admin import PlaceholderEditorAdmin
    from fluent_contents.analyzer import get_template_placeholder_data
    from .models import Page

    class PageAdmin(PlaceholderEditorAdmin):

        def get_placeholder_data(self, request, obj):
          # Tell the base class which tabs to create
            template = self.get_page_template(obj)
            return get_template_placeholder_data(template)


        def get_page_template(self, obj):
            # Simple example that uses the template selected for the page.
            if not obj:
                return get_template(appconfig.SIMPLECMS_DEFAULT_TEMPLATE)
            else:
                return get_template(obj.template_name or appconfig.SIMPLECMS_DEFAULT_TEMPLATE)

    admin.site.register(Page, PageAdmin)

Now, the placeholder editor will show itself with tabs for each placeholder.
The placeholder editor is implemented as inline, so it will be displayed nicely below
the standard forms.

The :func:`~fluent_contents.admin.PlaceholderEditorAdmin.get_placeholder_data` method instructs
the "placeholder editor" which tabbar items it should create.
It can use the :ref:`fluent_contents.analyzer` module for example to find the placeholders
in the template.

Variation for django-mptt
~~~~~~~~~~~~~~~~~~~~~~~~~

For CMS systems that are built with django-mptt_,
the same :class:`~fluent_contents.admin.PlaceholderEditorAdmin` can be used
thanks to the MRO (Method Resolution Order) that Python uses:

.. code-block:: python

    from mptt.admin import MPTTModelAdmin
    from fluent_contents.admin import PlaceholderEditorAdmin

    class PageAdmin(PlaceholderEditorAdmin, MPTTModelAdmin):

        # Same code as above

        def get_placeholder_data(self, request, obj):
            pass

Optional model enhancements
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The `Page` object of a CMS does not require any special fields.
Optionally, the :class:`~fluent_contents.models.PlaceholderRelation`
and :class:`~fluent_contents.models.ContentItemRelation` fields can be added
to allow traversing from the parent model to
the :class:`~fluent_contents.models.Placeholder`
and :class:`~fluent_contents.models.ContentItem` classes.

.. code-block:: python

    from django.db import models
    from fluent_contents.models import PlaceholderRelation, ContentItemRelation
    from . import appconfig


    class Page(models.Model):
        title = models.CharField("Title", max_length=200)
        template_name = models.CharField("Layout", max_length=255, choices=appconfig.SIMPLECMS_TEMPLATE_CHOICES)

        # ....

        placeholder_set = PlaceholderRelation()
        contentitem_set = ContentItemRelation()

Dynamic layout switching
------------------------

The ``example`` application also demonstrates how to switch layouts dynamically.
This happens fully client-side. Currently, the API of the "placeholder editor"
needs to be accessed directly, notably:

.. js:function:: cp_tabs.hide()

   Hide the content placeholder tab interface.
   This can be used in case no layout is selected.

.. js:function:: cp_tabs.expire_all_tabs()

   Hide the tabs, but don't remove them yet.
   This can be used when the new layout is being fetched;
   the old content will be hidden and is ready to move.

.. js:function:: cp_tabs.load_layout(layout)

   Load the new layout, this will create new tabs and move the existing
   content items to the new location.
   Content items are migrated to the apropriate placeholder,
   first matched by slot name, secondly matched by role.

   The ``layout`` parameter should be a JSON object with a structure like:

   .. code-block:: js

      var layout = {
          'placeholders': [
              {'title': "Main content", 'slot': "main", 'role': "m"},
              {'title': "Sidebar", 'slot': "sidebar", 'role': "s"},
          ]
      }

   The contents of each placeholder item is identical to
   what the :func:`~fluent_contents.models.PlaceholderData.as_dict` method
   of the :class:`~fluent_contents.models.PlaceholderData` class returns.

.. note::
    Currently the ``example`` application access the ``cp_tabs`` namespace directly.
    While this API is stable, a clean public API will likely be created in the future.


.. _django-mptt: https://github.com/django-mptt/django-mptt
