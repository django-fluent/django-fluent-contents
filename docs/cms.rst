.. _cms:

Creating a CMS system
=====================

Besides the :class:`~fluent_contents.models.PlaceholderField` class,
the `fluent_contents` module also provides additional admin classes to build a CMS interface.

The main difference between the CMS interface, and :class:`~fluent_contents.models.PlaceholderField`
class is that the placeholders will be created dynamically based on the template of the current page.
Instead of displaying placeholders inline in the form, the placeholder content is displayed
in a separate tabbar interface.

The features include:

* Detecting placeholders from a Django template.
* Automatically rearrange content items when the layout changes.
* Allow usage with any parent model.

In the source distribution, see the ``example.simplecms`` package for a working demonstration.

.. seealso::

    The django-fluent-pages_ application is built on top of this API, and provides a ready-to-use CMS that can be implemented with minimal configuration effort.
    To build a custom CMS, the API documentation of the :ref:`fluent_contents.admin` module provides more details of the classes.

The final appearance of the CMS would look something like:

    .. image:: /images/admin/placeholdereditoradmin1.png
       :width: 770px
       :height: 362px
       :alt: django-fluent-contents placeholder editor preview

Users can add various plugins to the page, for example by the DISQUS_ plugin:

    .. image:: images/admin/placeholdereditoradmin2.png
       :width: 755px
       :height: 418px
       :alt: django-fluent-contents placeholder editor preview


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

Now, the placeholder editor will show tabs for each placeholder.
The placeholder editor is implemented as a :class:`~django.contrib.admin.InlineModelAdmin`, so it will be displayed nicely below
the standard forms.

The :func:`~fluent_contents.admin.PlaceholderEditorAdmin.get_placeholder_data` method tells
the "placeholder editor" which tabbar items it should create.
It can use the :func:`~fluent_contents.analyzer.get_template_placeholder_data` function for example to find the placeholders
in the template.

Variation for django-mptt
~~~~~~~~~~~~~~~~~~~~~~~~~

For CMS systems that are built with django-mptt_,
the same :class:`~fluent_contents.admin.PlaceholderEditorAdmin` can be used
thanks to the method resolution order (MRO) that Python has:

.. code-block:: python

    from mptt.admin import MPTTModelAdmin
    from fluent_contents.admin import PlaceholderEditorAdmin

    class PageAdmin(PlaceholderEditorAdmin, MPTTModelAdmin):

        def get_placeholder_data(self, request, obj):
            # Same code as above
            pass

Optional model enhancements
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The `Page` object of a CMS does not require any special fields.

Optionally, the :class:`~fluent_contents.models.PlaceholderRelation`
and :class:`~fluent_contents.models.ContentItemRelation` fields can be added
to allow traversing from the parent model to
the :class:`~fluent_contents.models.Placeholder`
and :class:`~fluent_contents.models.ContentItem` classes.
This also causes the admin to display any :class:`~fluent_contents.models.Placeholder`
and :class:`~fluent_contents.models.ContentItem` objects that will be deleted on removing the page.

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
This happens entirely client-side. There is a public JavaScript API available to integrate with the layout manager.

.. js:function:: fluent_contents.layout.onInitialize(callback)

   Register a function this is called when the module initializes the layout for the first time.

   By letting the handler return ``true``, it will abort the layout initialization.
   The handler will be required to call ``fluent_contents.loadLayout()`` manually instead.
   This feature is typically used to restore a previous client-side selection of the user,
   instead of loading the last known layout at the server-side.

.. js:function:: fluent_contents.layout.expire()

   Hide the placeholder tabs, but don't remove them yet.
   This can be used when the new layout is being fetched;
   the old content will be hidden and is ready to move.

.. js:function:: fluent_contents.layout.load(layout)

   Load the new layout, this will create new tabs and move the existing content items to the new location.
   Content items are migrated to the apropriate placeholder, first matched by slot name, secondly matched by role.

   The ``layout`` parameter should be a JSON object with a structure like:

   .. code-block:: js

      var layout = {
          'placeholders': [
              {'title': "Main content", 'slot': "main", 'role': "m", 'allowed_plugins': ["TextPlugin"]},
              {'title': "Sidebar", 'slot': "sidebar", 'role': "s", 'fallback_language': true, 'allowed_plugins': ["TextPlugin", "PicturePlugin"]},
          ]
      }

   The contents of each placeholder item is identical to
   what the :func:`~fluent_contents.models.PlaceholderData.as_dict` method
   of the :class:`~fluent_contents.models.PlaceholderData` class returns.

.. js:function:: fluent_contents.tabs.show(animate)

   Show the content placeholder tab interface.

.. js:function:: fluent_contents.tabs.hide(animate)

   Hide the content placeholder tab interface.
   This can be used in case no layout is selected.

.. note::

   Other JavaScript functions of the content placeholder editor that live outside the ``fluent_contents`` namespace
   are private, and may be changed in future releases.


.. _DISQUS: http://disqus.com
.. _django-mptt: https://github.com/django-mptt/django-mptt
.. _django-fluent-pages: https://github.com/django-fluent/django-fluent-pages
