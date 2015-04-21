fluent_contents.extensions
==========================

.. automodule:: fluent_contents.extensions

The ``ContentPlugin`` class
---------------------------

.. autoclass:: fluent_contents.extensions.ContentPlugin
   :members:

The ``PluginPool`` class
------------------------

.. autoclass:: fluent_contents.extensions.PluginPool
   :members:

The ``plugin_pool`` attribute
-----------------------------

.. attribute:: fluent_contents.extensions.plugin_pool

    The global plugin pool, a instance of the :class:`PluginPool` class.


Model fields
------------

.. versionadded:: 0.9.0

The model fields ensure a consistent look and feel between plugins.
It's recommended to use these fields instead of the standard Django counterparts,
so all plugins have a consistent look and feel.
See :ref:`optional-integration` for more details.

.. autoclass:: fluent_contents.extensions.PluginFileField
   :members:

.. autoclass:: fluent_contents.extensions.PluginHtmlField
   :members:

.. autoclass:: fluent_contents.extensions.PluginImageField
   :members:

.. autoclass:: fluent_contents.extensions.PluginUrlField
   :members:


Classes for custom forms
------------------------

.. versionadded:: 0.9.0
   The canonical place to import this class has moved, previously it was available via :mod:`fluent_contents.forms`.

.. autoclass:: fluent_contents.extensions.ContentItemForm
   :members:


Other classes
-------------

.. autoclass:: fluent_contents.extensions.PluginContext
   :members:

.. autoexception:: fluent_contents.extensions.PluginAlreadyRegistered

.. autoexception:: fluent_contents.extensions.PluginNotFound

