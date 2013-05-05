.. _configuration:

Configuration
=============

A quick overview of the available settings:

.. code-block:: python

    FLUENT_CONTENTS_CACHE_OUTPUT = True

    FLUENT_CONTENTS_PLACEHOLDER_CONFIG = {
        'slot_name': {
            'plugins': ('TextPlugin', 'PicturePlugin', 'OEmbedPlugin', 'SharedContentPlugin', 'RawHtmlPlugin',)
        },
        'shared_content': {
            'plugins': ('TextPlugin',)
        }
        'blog_contents': {
            'plugins': ('TextPlugin', 'PicturePlugin',)
        }
    }


.. _FLUENT_CONTENTS_CACHE_OUTPUT:

FLUENT_CONTENTS_CACHE_OUTPUT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, the HTML output of all plugins is cached.
The output is only updated when a staff member saves changes in in the Django admin.
Caching greatly improves the performance of the web site, as very little database queries are needed.
Most pages look the same for every visitor anyways.

In case this conflicts with your caching setup,
disable this feature side-wide by setting this flag to ``False``.


.. _FLUENT_CONTENTS_PLACEHOLDER_CONFIG:

FLUENT_CONTENTS_PLACEHOLDER_CONFIG
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This setting limits which plugins can be used in a given placeholder slot.
For example, a "homepage" slot may include add a "slideshow", while the "sidebar" slot can be limited to other elements.
By default, all plugins are allowed to be used everywhere.

The list of plugins can refer to class names, or point to the actual classes themselves.
When a list of plugins is explicitly passed to a :class:`~fluent_contents.models.PlaceholderField`,
it overrides the defaults given via the settings file.
