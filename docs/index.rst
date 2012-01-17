Welcome to django-fluent-contents' documentation!
=================================================

This documentation covers the latest release of django-fluent-contents, a collection of applications
to build an end user CMS for the `Django <http://www.djangoproject.com>`_ administration interface.
django-fluent-contents includes:

* A ``PlaceholderField`` to display various content on a model.
* A ``PlaceholderEditorAdmin`` to build CMS interfaces.
* A default set of plugins to display WYSIWYG content, reStructuredText, highlighted code, Gist snippets and more.
* an extensible plugin API.

To get up and running quickly, consult the :ref:`quick-start guide <quickstart>`.
The chapters below describe the configuration of each specific plugin in more detail.


Getting started
---------------

.. toctree::
   :maxdepth: 2

   quickstart
   newplugins

Content plugins
---------------

Standard plugins:

.. toctree::
   :maxdepth: 2

   plugins/text

Interactivity:

.. toctree::
   :maxdepth: 2

   plugins/commentsarea
   plugins/disquscommentsarea
   plugins/formdesignerlink

Online services:

.. toctree::
   :maxdepth: 2

   plugins/googledocsviewer

Programming:

.. toctree::
   :maxdepth: 2

   plugins/code
   plugins/gist
   plugins/markup

Advanced:

.. toctree::
   :maxdepth: 2

   plugins/iframe
   plugins/rawhtml

Advanced topics
---------------

.. toctree::
   :maxdepth: 2

   cms

API documentation
-----------------

.. toctree::
   :maxdepth: 2

   api/admin
   api/analyzer
   api/extensions
   api/forms
   api/managers
   api/models
   api/rendering
   api/templatetags/placeholder_tags
   api/utils

Roadmap
=======

The following features are planned:

* Frontend editing support
* Global / shared placeholders
* Fieldsets in plugins
* Caching output of content items in memcached (updated on admin edit).
* Gracefully handle errors when removing plugins (currently causes errors in *django-polymorphic* / *django.contrib.contenttypes*)
* Bridging other plugin systems, like Django CMS
* Inline support (e.g. building a linklist plugin).

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

