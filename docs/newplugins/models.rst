.. _newplugins-example:

Example plugin code
===================

A plugin is a standard Django/Python package.
As quick example, let's create an announcement block.

This is a typical module that is found on many websites; a title text, some intro text and "call to action" button at the bottom.
Such item could be created in a WYSIWYG editor, but in this case we'll provide a clear interface for the editorial content.

The plugin can be created in your Django project, in a separate app
which can be named something like ``plugins.announcementblock`` or ``mysite.contentitems``.

Example code
------------

For the ``plugins.announcementblock`` package, the following files are needed:

* ``__init__.py``, naturally.
* ``models.py`` for the database model.
* ``content_plugins.py`` for the plugin definition.

models.py
~~~~~~~~~

The models in :file:`models.py` needs to inherit from the :class:`~fluent_contents.models.ContentItem` class,
the rest is just standard Django model code.

.. code-block:: python

  from django.db import models
  from django.utils.translation import ugettext_lazy as _
  from fluent_contents.models import ContentItem

  class AnnouncementBlockItem(ContentItem):
      """
      Simple content item to make an announcement.
      """
      title = models.CharField(_("Title"), max_length=200)
      body = models.TextField(_("Body"))

      button_text = models.CharField(_("Text"), max_length=200)
      button_link = models.URLField(_("URL"))

      class Meta:
          verbose_name = _("Announcement block")
          verbose_name_plural = _("Announcement blocks")

      def __unicode__(self):
          return self.title

This :class:`~fluent_contents.models.ContentItem` class provides the basic fields to integrate the model in a placeholder.
The ``verbose_name`` and ``__unicode__`` fields are required to display the model in the admin interface.

content_plugins.py
~~~~~~~~~~~~~~~~~~

The :file:`content_plugins.py` file can contain multiple plugins, each should inherit from the :class:`~fluent_contents.extensions.ContentPlugin` class.

.. code-block:: python

  from django.utils.translation import ugettext_lazy as _
  from fluent_contents.extensions import plugin_pool, ContentPlugin
  from .models import AnnouncementBlockItem


  @plugin_pool.register
  class AnnouncementBlockPlugin(ContentPlugin):
     model = AnnouncementBlockItem
     render_template = "plugins/announcementblock.html"
     category = _("Simple blocks")
     cache_output = False    # Temporary set for development

     fieldsets = (
         (None, {
             'fields': ('title', 'body',)
         }),
         (_("Button"), {
             'fields': ('button_text', 'url',)
         })
     )


The plugin class binds all parts together; the model, metadata, and rendering code.
Either the :func:`~fluent_contents.extensions.ContentPlugin.render` function can be overwritten, or a :attr:`~fluent_contents.extensions.ContentPlugin.render_template` can be defined.

The other fields, such as the :attr:`~fluent_contents.extensions.ContentPlugin.fieldsets` are optional.
The :func:`plugin_pool.register <fluent_contents.extensions.PluginPool.register>` decorator registers the plugin.


announcementblock.html
~~~~~~~~~~~~~~~~~~~~~~

The default :func:`~fluent_contents.extensions.ContentPlugin.render` code makes the model instance available as the ``instance`` variable.
This can be used to generate the HTML:

.. code-block:: html+django

    <div class="announcement">
        <h3>{{ instance.title }}</h3>
        <div class="text">
            {{ instance.body|linebreaks }}
        </div>
        <p class="button"><a href="{{ instance.button_url }}">{{ instance.button_text }}</a></p>
    </div>

.. important::

    By default, the output of plugins is cached; changes to the template file
    are only visible when the model is saved in the Django admin.
    You can set :ref:`FLUENT_CONTENTS_CACHE_OUTPUT` to ``False``, or use 
    the :attr:`~fluent_contents.extensions.ContentPlugin.cache_output` setting temporary in development.
    The setting is enabled by default to let plugin authors make a conscious decision about caching
    and avoid unexpected results in production.

Wrapping up
~~~~~~~~~~~

The plugin is now ready to use.
Don't forget to add the ``plugins.announcementblock`` package to the ``INSTALLED_APPS``, and create the tables::

    ./manage.py syncdb

Now, the plugin will be visible in the editor options:

.. image:: /images/newplugins/announcementblock-addpopup.png
   :width: 200px
   :height: 260px
   :scale: 95
   :alt: New announcement block in the popup

After adding it, the admin interface will be visible:

.. image:: /images/newplugins/announcementblock-admin.png
  :width: 956px
  :height: 330px
  :scale: 75
  :alt: Announcement block admin interface

The appearance at the website, depends on the sites CSS theme off course.

This example showed how a new plugin can be created within 5-15 minutes!
To continue, see :doc:`rendering` to implement custom rendering.
