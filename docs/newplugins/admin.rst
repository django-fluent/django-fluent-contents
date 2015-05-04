.. _newplugins-admin:

Customizing the admin interface
===============================

The admin rendering of a plugin is - by design - mostly controlled outside the plugin class.
However, the :class:`~fluent_contents.extensions.ContentPlugin` class does provide
a controlled set of options to configure the admin interface.
For example, the :attr:`~fluent_contents.extensions.ContentPlugin.fieldsets` attribute
was already mentioned in the previous :doc:`example code <models>` page:

.. code-block:: python

    @plugin_pool.register
    class AnnouncementBlockPlugin(ContentPlugin):
       model = AnnouncementBlockItem
       render_template = "plugins/announcementblock.html"
       category = _("Simple blocks")

       fieldsets = (
           (None, {
               'fields': ('title', 'body',)
           }),
           (_("Button"), {
               'fields': ('button_text', 'url',)
           })
       )

The other options are documented here.

Internally, the plugin is rendered in the admin as an inline model, but this is out of scope for the plugin code.
In a different context (e.g. frontend editing) this could easily by replaced by another container format.


General metadata
----------------

The following attributes control the appearance in the plugin ``<select>`` box:

* :attr:`~fluent_contents.extensions.ContentPlugin.verbose_name` -
  The title of the plugin, which reads the ``verbose_name`` of the model by default.

* :attr:`~fluent_contents.extensions.ContentPlugin.category` -
  The title of the category.


Changing the admin form
-----------------------

The following attributes control the overall appearance of the plugin in the admin interface:

* :attr:`~fluent_contents.extensions.ContentPlugin.admin_form_template` -
  The template to render the admin interface with.

* :attr:`~fluent_contents.extensions.ContentPlugin.admin_init_template` -
  This optional template is inserted once at the top of the admin interface.

* :attr:`~fluent_contents.extensions.ContentPlugin.form` -
  The form class to use in the admin form. It should inherit from the :class:`~fluent_contents.extensions.ContentItemForm` class.

* :attr:`~fluent_contents.extensions.ContentPlugin.fieldsets` -
  A tuple of fieldsets, similar to the :class:`~django.contrib.admin.ModelAdmin` class.


The :attr:`~fluent_contents.extensions.ContentPlugin.admin_form_template` is used for example
by the :ref:`code <code>` plugin. It displays the "language" and "line number" fields at a single line.
Other plugins, like the :ref:`rawhtml <rawhtml>` and :ref:`text <text>` plugins use
this setting to hide the form labels. The available templates are:

* ``admin/fluent_contents/contentitem/admin_form.html`` (the default template)
* ``admin/fluent_contents/contentitem/admin_form_without_labels.html`` aka
  :attr:`ContentPlugin.ADMIN_TEMPLATE_WITHOUT_LABELS <fluent_contents.extensions.ContentPlugin.ADMIN_TEMPLATE_WITHOUT_LABELS>`.

The :attr:`~fluent_contents.extensions.ContentPlugin.admin_init_template` can be used
by plugins that need to add some template-based initialization.
The :ref:`text <text>` plugin uses this for example to initialize the WYSIWYG editor.


Changing the admin fields
-------------------------

The following attributes control the overall appearance of form fields in the admin interface:

* :attr:`~fluent_contents.extensions.ContentPlugin.raw_id_fields` -
  A tuple of field names, which should not be displayed as a selectbox, but as ID field.

* :attr:`~fluent_contents.extensions.ContentPlugin.filter_vertical` -
  A tuple of field names to display in a vertical filter.

* :attr:`~fluent_contents.extensions.ContentPlugin.filter_horizontal` -
  A tuple of field names to display in a horizontal filter.

* :attr:`~fluent_contents.extensions.ContentPlugin.radio_fields` -
  A dictionary listing all fields to display as radio choice.
  The key is the field name, the value can be ``admin.HORIZONTAL`` / ``admin.VERTICAL``.

* :attr:`~fluent_contents.extensions.ContentPlugin.prepopulated_fields` -
  A dictionary listing all fields to auto-complete. This can be used for slug fields,
  and works identically to the :attr:`~django.contrib.admin.ModelAdmin.prepopulated_fields` attribute of the :class:`~django.contrib.admin.ModelAdmin` class.

* :attr:`~fluent_contents.extensions.ContentPlugin.formfield_overrides` -
  A dictionary to override form field attributes. Unlike the regular :class:`~django.contrib.admin.ModelAdmin` class,
  both classes and field names can be used as dictionary key.
  For example, to specify the :attr:`~django.forms.IntegerField.max_value` of an :class:`~django.forms.IntegerField` use:

  .. code-block:: python

      formfield_overrides = {
          'fieldname': {
              'max_value': 900
          },
      }

* :attr:`~fluent_contents.extensions.ContentPlugin.readonly_fields` -
  A list of fields to display as readonly.


.. _custom-model-fields:

Custom model fields
-------------------

.. versionadded:: 0.9.0

To maintain consistency between plugins, this package provides a few additional model fields which plugins can use.
By default, these fields use the standard Django model fields. When one of the :ref:`optional packages <optional-integration>`
is installed, the fields will use those additional features:

* :class:`fluent_contents.extensions.PluginFileField` -
  The file field uses :class:`~django.db.models.FileField` by default. It displays a file browser when django-any-imagefield_ is installed.

* :class:`fluent_contents.extensions.PluginHtmlField` -
  The HTML field displays the WYSIWYG editor, which is also used by the :ref:`text plugin <text>`.

* :class:`fluent_contents.extensions.PluginImageField` -
  The file field uses :class:`~django.db.models.ImageField` by default. It displays a file browser when django-any-imagefield_ is installed.

* :class:`fluent_contents.extensions.PluginUrlField` -
  The URL field uses :class:`~django.db.models.URLField` by default. It displays a URL selector for internal models when django-any-urlfield_ is installed.

Whenever your plugin uses an image field, file field, WISYWIG editor, or URL field that may refer to internal URL's,
consider using these classes instead of the regular Django fields.


Adding CSS to the admin interface
---------------------------------

The plugin allows to define a ``class Media`` with the CSS files to include in the admin interface.
For example:

.. code-block:: python

    class Media:
        css = {
            'screen': ('plugins/myplugin/plugin_admin.css',)
        }

By default, all paths are relative to the ``STATIC_URL`` of the Django project.

Each content item has a ``.inline-ModelName`` class in the admin interface.
This can be used to apply CSS rules to the specific plugin only.

For example, the ``<textarea>`` of a ``RawHtmlItem`` model form can be styled using:

.. code-block:: css

  .inline-RawHtmlItem textarea.vLargeTextField {
    /* allow the OS to come up with something better then Courier New */
    font-family: "Consolas", "Menlo", "Monaco", "Lucida Console", "Liberation Mono", "DejaVu Sans Mono", "Bitstream Vera Sans Mono", "Courier New", monospace;
    padding: 5px; /* 3px is standard */
    width: 606px;
  }



Adding JavaScript behavior
--------------------------

In a similar way, JavaScript can be added to the admin interface:

.. code-block:: python

    class Media:
        js = (
            'plugins/myplugin/plugin_admin.js',
        )

Note however, that content items can be dynamically added or removed in the admin interface.
Hence the JavaScript file should register itself as "view handler".
A view handler is called whenever the user adds or removes a content item in the admin interface.

In case of the Announcement Block plugin, the general layout of the file would look like:

.. code-block:: javascript

    (function($){

      var AnnouncementBlockHandler = {

          enable: function($contentitem) {
              var inputs = $contentitem.find("input");
              // ... update the items
          },

          disable: function($contentitem) {
              // deinitialize, if needed
          }
      };

      // Register the view handler for the 'AnnouncementBlockItem' model.
      fluent_contents.plugins.registerViewHandler('AnnouncementBlockItem', AnnouncementBlockHandler);

    })(window.jQuery || django.jQuery);

This mechanism can be used to initialize a WYSIWYG editor, or bind custom events to the DOM elements for example.
While it's not demonstrated by the current bundled plugins, you can implement an inline preview/edit switch this way!

The view handler is a JavaScript object, which should have the following methods:

.. js:function:: enable($contentitem)

   The :func:`enable` function is called whenever the user adds the content item.
   It receives a ``jQuery`` object that points to the root of the content item object in the DOM.

.. js:function:: disable($contentitem)

   The :func:`disable` function is called just before the user removes the content item.
   It receives a ``jQuery`` object that points to the root of the content item object in the DOM.

.. js:function:: initialize($formset_group)

   The :func:`initialize` function is not required. In case it exists, it will be called once at the start of the page.
   It's called right after all plugins are initialized, but just before they are moved to the proper location in the DOM.

Note that the :func:`enable` and :func:`disable` functions can be called multiple times,
because it may also be called when a content item is moved to another placeholder.

In the :func:`initialize` function, the following jQuery selectors can be used:

* ``.inline-contentitem-group`` selects all formsets which contain content item forms.
* ``.inline-ModelName-group`` selects the formset which contain the content items of a plugin.
* ``.inline-ModelName`` selects each individual formset item in which a form is displayed, including the empty form placeholder.
* ``.inline-ModelName:not(.empty-form)`` selects all active formset items.
* ``.inline-ModelName.empty-form`` selects the placeholder formset which is used to create new items.

After the :func:`initialize` function has run, the items are moved to the apropriate placeholders,
so the group selectors can only select all items reliably in the :func:`initialize` function.
The other selectors remain valid, as they operate on individual elements.


.. _django-any-urlfield: https://github.com/edoburu/django-any-urlfield
.. _django-any-imagefield: https://github.com/edoburu/django-any-imagefield
