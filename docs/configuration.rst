.. _configuration:

Configuration
=============

A quick overview of the available settings:

.. code-block:: python

    FLUENT_CONTENTS_CACHE_OUTPUT = True               # disable sometimes for development
    FLUENT_CONTENTS_CACHE_PLACEHOLDER_OUTPUT = False  # enable for production

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

    FLUENT_CONTENTS_DEFAULT_LANGUAGE_CODE = LANGUAGE_CODE  # e.g. "en"
    FLUENT_CONTENTS_FILTER_SITE_ID = True


Rendering options
-----------------

.. _FLUENT_CONTENTS_CACHE_OUTPUT:

FLUENT_CONTENTS_CACHE_OUTPUT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Typically, most web site pages look the same for every visitor.
Hence, this module takes the following default policies:

* the output of plugins is cached by default.
* the cache is refreshed when a staff member updates saves changes in in the Django admin.
* each :class:`~fluent_contents.extensions.ContentPlugin` can specify custom :ref:`caching settings <output-caching>` to influence this.
* caching is even enabled for development (to test production setup), but changes in templates are detected.

Caching greatly improves the performance of the web site, as very little database queries are needed.
If you have a few custom plugins that should not be cached per request (e.g. a contact form),
update the :ref:`output caching <output-caching>` settings of that specific plugin.

However, in case this is all too complex, you can disable the caching mechanism entirely.
The caching can be disabled by setting this option to ``False``.

.. _FLUENT_CONTENTS_CACHE_PLACEHOLDER_OUTPUT:

FLUENT_CONTENTS_CACHE_PLACEHOLDER_OUTPUT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This setting can be used to enable the output of entire placeholders.
Preferably, this should be enabled for production.

This feature is impractical in development, because any changes to code or templates won't appear.
Hence, the default value is ``False``.

Without this setting, only individual content plugins are cached.
The surrounding objects will still be queried from the database.
That includes:

 * The :class:`~fluent_contents.models.Placeholder`
 * Any :class:`~fluent_contents.plugins.sharedcontent.models.SharedContent` model.
 * The base class of each :class:`~fluent_contents.models.ContentItem` model.

.. _FLUENT_CONTENTS_DEFAULT_LANGUAGE_CODE:

FLUENT_CONTENTS_DEFAULT_LANGUAGE_CODE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The default language for items. This value is used as:

* The fallback language for rendering content items.
* The default language for the :attr:`ContentItem.language_code <fluent_contents.models.ContentItem.language_code>` model field
  when the parent object is not translatable.
* The initial migration of data when you migrate a 0.9 project to v1.0

When this value is not defined, the following settings will be tried:

* ``FLUENT_DEFAULT_LANGUAGE_CODE``
* ``PARLER_DEFAULT_LANGUAGE_CODE``
* ``LANGUAGE_CODE``


HTML Field Settings
-------------------

.. _FLUENT_TEXT_CLEAN_HTML:

FLUENT_TEXT_CLEAN_HTML
~~~~~~~~~~~~~~~~~~~~~~

If ``True``, the HTML content returned by the :class:`~fluent_contents.extensions.PluginHtmlField`
will be rewritten to be well-formed using html5lib_.

.. _FLUENT_TEXT_SANITIZE_HTML:

FLUENT_TEXT_SANITIZE_HTML
~~~~~~~~~~~~~~~~~~~~~~~~~

if ``True``, unwanted HTML tags will be removed server side using html5lib_.


.. _FLUENT_TEXT_POST_FILTERS:
.. _FLUENT_TEXT_PRE_FILTERS:

FLUENT_TEXT_POST_FILTERS, FLUENT_TEXT_PRE_FILTERS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These settings accept a list of callable function names,
which are called to update the HTML content.
For example:

.. code-block:: python

   FLUENT_TEXT_PRE_FILTERS = (
      'myapp.filters.cleanup_html',
      'myapp.filters.validate_html',
      'fluent_contents.plugins.text.filters.smartypants.smartypants_filter',
   )

   FLUENT_TEXT_POST_FILTERS = (
      'fluent_contents.plugins.text.filters.softhypen.softhypen_filter',
   )

The pre-filters and post-filters differ in a slight way:

* The *pre*-filters updates the source text, so they should be idempotent.
* The *post*-filters only affect the displayed output, so they may manipulate the HTML completely.

.. seealso::
   The :doc:`filters` documentation.


Admin settings
--------------

.. _FLUENT_CONTENTS_PLACEHOLDER_CONFIG:

FLUENT_CONTENTS_PLACEHOLDER_CONFIG
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This setting limits which plugins can be used in a given placeholder slot.
For example, a "homepage" slot may include add a "slideshow", while the "sidebar" slot can be limited to other elements.
By default, all plugins are allowed to be used everywhere.

The list of plugins can refer to class names, or point to the actual classes themselves.
When a list of plugins is explicitly passed to a :class:`~fluent_contents.models.PlaceholderField`,
it overrides the defaults given via the settings file.


Advanced admin settings
-----------------------


.. _FLUENT_CONTENTS_FILTER_SITE_ID:

FLUENT_CONTENTS_FILTER_SITE_ID
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, contents is displayed for the current site only.

By default, each :class:`~django.contrib.sites.models.Site` model has it's own contents.
This enables the multi-site support, where you can run multiple instances with different sites.
To run a single Django instance with multiple sites, use a module such as django-multisite_.

You can disable it using this by using:

.. code-block:: python

    FLUENT_PAGES_FILTER_SITE_ID = False

This completely disables the multisite support, and should only be used as last resort.
The :class:`~fluent_contents.plugins.sharedcontent.models.SharedContent` model
is unsplit, making all content available for all sites.

.. note::
   The "Shared Content" module also provides a "Share between all sites" setting to share a single object explicitly
   between multiple sites. Enable it using the :ref:`FLUENT_SHARED_CONTENT_ENABLE_CROSS_SITE` setting.
   Using that feature is recommended above disabling multisite support completely.


.. _html5lib: http://code.google.com/p/html5lib/
.. _django-multisite: https://github.com/ecometrica/django-multisite
