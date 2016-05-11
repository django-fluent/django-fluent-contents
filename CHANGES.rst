Changelog
=========

Changes in 1.1.3 (2016-05-11)
-----------------------------

* Fixed ``{% csrf_token %}`` support in plugin templates.
* Fixed django-debug-toolbar_ support for skipped items.
* Fixed error handling of missing content items in the database.


Changes in 1.1.2 (2016-03-25)
-----------------------------

* Fix truncating long ``db_table`` names, just like Django does.
* Fix various Django 1.9 warnings that would break once Django 1.10 is out.
* Enforce newer versions on dependencies to ensure all bugfixes are installed.


Changes in 1.1.1 (2016-01-04)
-----------------------------

* Fixed errors when rendering pages with missing items


Changes in 1.1 (2015-12-29)
---------------------------

* Added Django 1.9 support
* Added django-debug-toolbar_ panel: ``fluent_contents.panels.ContentPluginPanel'``.
* Added ``Placeholder.get_search_text()`` API for full text indexing support.
* Added ``FLUENT_TEXT_POST_FILTERS`` and ``FLUENT_TEXT_PRE_FILTERS`` to the text plugin for further processing of the text.
* **BACKWARDS INCOMPATIBLE:** as text filters became global, the settings in :mod:`fluent_contents.plugins.text.appsettings` moved to :mod:`fluent_contents.appsettings`.
* Dropped Django 1.4 support


Changes in 1.0.4 (2015-12-17)
-----------------------------

* Prevent caching complete placeholder/sharedcontent output when there are items with ``cache_output_per_site``.
  This only occurs in environments where ``FLUENT_CONTENTS_CACHE_PLACEHOLDER_OUTPUT`` is enabled.
* Fix Django migration unicode issues in Python 3
* Fix error in ``get_output_cache_keys()`` when reading the ``pk`` field during deletion.
* Fix compatibility with django-polymorphic_ 0.8.


Changes in 1.0.3 (2015-10-01)
-----------------------------

* Improve styling with django-flat-theme_ theme.
* Fix choices listing of the "Copy Language" button.
* Fix form field order so CSS can select ``.form-row:last-child``.


Version 1.0.2
-------------

* Added ``ContentItem.move_to_placeholder()`` and ``ContentItem.objects.move_to_placeholder()`` API functions
* Added check against bad html5lib versions that break HTML cleanup.
* Fix using ``ContentItemInline.get_queryset()`` in Django 1.6/1.7/1.8
* Fix Python 3.4 support for development (fixed ``_is_template_updated`` / "is method overwritten" check)
* Fix support for returning an ``HttpRedirectRequest`` in the ``ContentPlugin.render()`` method.
* Fix ``copy_to_placeholder()`` to accidently setting an empty "FK cache" entry for the ``ContentItem.parent`` field.
* Fix ``TypeError`` when abstract ``ContentItem`` class has no ``__str__()`` method.
* Fix initial migration for sharedcontent plugin.
* Fix handling of ``SharedContent.__str__()`` for missing translations.


Version 1.0.1
-------------

* Fix rendering in development for Django 1.4 and 1.5
* Fix placeholder cache timeout values, take ``ContentPlugin.cache_output`` into account.
  This is only an issue when using ``FLUENT_CONTENTS_CACHE_PLACEHOLDER_OUTPUT = True``.
* Fix migration files that enforced using django-any-urlfield_ / django-any-imagefield_.
  NOTE: all migrations now explicitly refer to ``PluginUrlField`` / ``PluginImageField``.
  You can either generate new Django migrations, or simply replace the imports in your existing migrations.


Version 1.0
-----------

* Added Django 1.8 support.
* Added caching support for the complete ``{% render_placeholder %}``, ``{% page_placeholder %}`` and ``{% sharedcontent %}`` tags.
* Added ``as var`` syntax for ``{% render_placeholder %}``, ``{% page_placeholder %}`` and ``{% sharedcontent %}`` tags.
* Added ``ContentItem.copy_to_placeholder()`` and ``ContentItem.objects.copy_to_placeholder()`` API functions
* Fix handling ``CheckboxSelectMultiple`` in admin form widgets.
* Fix missing API parameters for ``ContentItem.objects.create_for_placeholder()`` and ``Placeholder.objects.create_for_parent()``.
* Fix static default ``SITE_ID`` value for ``SharedContent``, for compatibility with django-multisite_.
* Fix cache invalidation when using ``render_ignore_item_language``.
* Fix adding a second ``PlaceholderField`` to a model in a later stage.


Released on 1.0c3:
~~~~~~~~~~~~~~~~~~

* Added Django 1.7 support.
* Added option to share ``SharedContent`` objects across multiple websites.
* Allow passing ``SharedContent`` object to ``{% sharedcontent %}`` template tag.
* Added ``SharedContent.objects.published()`` API for consistency between all apps.
* Fixed rendering content items in a different language then the object data is saved as.
  This can be overwritten by using ``render_ignore_item_language = True`` in the plugin.
* Fixed support for: future >= 0.13.
* Improve default value of ``ContentPlugin.cache_timeout`` for Django 1.6 support.
* Fix frontend media support for ``{% sharedcontent %}`` tag.
* **BACKWARDS INCOMPATIBLE:** South 1.0 is required to run the migrations (or set ``SOUTH_MIGRATION_MODULES`` for all plugins).
* **BACKWARDS INCOMPATIBLE:** Content is rendered in the language that is is being saved as, unless ``render_ignore_item_language`` is set.

.. note::
   Currently, Django 1.7 doesn't properly detect the generated ``db_table`` value properly for ContentItem objects.
   This needs to be added manually in the migration files.


Released on 1.0c2:
~~~~~~~~~~~~~~~~~~

* Fix JavaScript errors with ``for i in`` when ``Array.prototype`` is extended.
  (e.g. when using django-taggit-autosuggest_).


Released on 1.0c1:
~~~~~~~~~~~~~~~~~~

* Fix saving content item sorting.


Released on 1.0b2:
~~~~~~~~~~~~~~~~~~

* Added Python 3 support!
* Fixed Django 1.6 compatibility.
* Fixed disappearing contentitems issue for PlaceholderField on add-page
* Fixed orphaned content for form errors in the add page.
* Fixed no tabs selected on page reload.


Released on 1.0b1:
~~~~~~~~~~~~~~~~~~

* Added multilingual support, using django-parler_.
* Added multisite support to sharedcontent plugin.
* Added frontend media support.
* Added "Open in new window" option for the "picture" plugin.
* Added ``HttpRedirectRequest`` exception and ``HttpRedirectRequestMiddleware``.
* Added ``cache_output_per_language`` option to plugins.
* Content items are prefixed with "content:" during syncdb, a ``prefix_content_item_types`` management command can be run manually too.
* **API Change:** Renamed template tag library ``placeholder_tags`` to ``fluent_contents_tags`` (the old name still works).
* **API Change:** ``render_placeholder()`` and ``render_content_items()`` return a ``ContentItemOutput`` object, which can be treated like a string.
* **API Change:** both ``get_output_cache_key()`` and ``get_output_cache_keys()`` should use ``get_output_cache_base_key()`` now.
* Fix showing non-field-errors for inlines.
* Fix server error on using an invalid OEmbed URL.
* Fix gist plugin, allow UUID's now.
* Fix missing ``alters_data`` annotations on model methods.
* Removed unneeded ``render_comment_list`` templatetag as it was upstreamed to django-threadedcomments_ 0.9.


Version 0.9
-------------

* Dropped Django 1.3 support, added Django 1.6 support.
* Added ``FLUENT_CONTENTS_PLACEHOLDER_CONFIG`` variable to limit plugins in specific placeholder slots.
* Added model fields for plugin developers, to have a consistent interface.
  The model fields integrate with django-any-urlfield_, django-any-imagefield_ and django-wysiwyg_.
* Added picture plugin.
* Added development (``DEBUG=True``) feature, changes in plugin templates update the stored version in the output cache.
* Added cache methods to plugins which can be overwritten (``get_output_cache_key()``, ``get_cached_output()``, etc..)
* Added ``cache_output_per_site`` option to plugins.
* Fix admin appearance of plugins without fields.
* Fix initial south migrations, added missing dependencies.


Version 0.8.6
-------------

* Fixed metaclass errors in markup plugin for Django 1.5 / six.
* Fix initial south migrations, added missing dependencies.
* Fixed cache clearing of sharedcontent plugin.
* Updated django-polymorphic_ version to 0.4.2, addressed deprecation warnings.
* Updated example app to show latest features.


Version 0.8.5
-------------

* Added support for shared content.
* Added ``ContentPlugin.HORIZONTAL`` and ``ContentPlugin.VERTICAL`` constants for convenience.
* Added support for noembed_ in ``FLUENT_OEMBED_SOURCE`` setting.
* Added ``FLUENT_OEMBED_EXTRA_PROVIDERS`` setting to the OEmbed plugin.
* Fix Django 1.5 compatibility.
* Fix *code* plugin compatibility with Pygments 1.6rc1.
* Fix escaping slot name in templates
* Fix https support for OEmbed plugin.
* Fix maxwidth parameter for OEmbed plugin.
* Fix updating OEmbed code after changing maxwidth/maxheight parameters.
* Moved the template tag parsing to a separate package, django-tag-parser_.
* Bump version of django-wysiwyg_ to 0.5.1 because it fixes TinyMCE integration.
* Bump version of micawber_ to 0.2.6, which contains an up to date list of known OEmbed providers.
* **BIC:** As micawber_ is actively updated, we no longer maintain a local list of known OEmbed providers.
  This only affects installations where ``FLUENT_OEMBED_SOURCE = "list"`` was explicitly defined in ``settings.py``,
  without providing a list for ``FLUENT_OEMBED_PROVIDER_LIST``. The new defaults are: ``FLUENT_OEMBED_SOURCE = "basic"``
  and ``FLUENT_OEMBED_PROVIDER_LIST = ()``.


Version 0.8.4
-------------

* Fix 500 error when content items get orphaned after switching layouts.
* Fix plugin dependencies installation via the optional dependency specifier (e.g. ``django-fluent-contents[text]``).
* Fix missing dependency check for OEmbed plugin
* Fix Django dependency in ``setup.py``, moved from ``install_requires`` to the ``requires`` section.
* Fix template name for django-threadedcomments_ to ``comment/list.html``,
  to be compatible with the pull request at https://github.com/HonzaKral/django-threadedcomments/pull/39.


Version 0.8.3
-------------

* Fixed ``fluent_contents.rendering.render_content_items()`` to handle models without a PK.
* Make sure the client-side ``sort_order`` is always consistent, so external JS code can read/submit it.


Version 0.8.2
-------------

* Fixed ``PlaceholderField`` usage with inherited models.


Version 0.8.1
-------------

* Fixed missing files for oembed and markup plugins.
* Clarified documentation bits


Version 0.8.0
-------------

First PyPI release.

The module design has been stable for quite some time,
so it's time to show this module to the public.


.. _django-any-urlfield: https://github.com/edoburu/django-any-urlfield
.. _django-any-imagefield: https://github.com/edoburu/django-any-imagefield
.. _django-flat-theme: https://github.com/elky/django-flat-theme
.. _django-parler: https://github.com/edoburu/django-parler
.. _django-polymorphic: https://github.com/chrisglass/django_polymorphic
.. _django-multisite: https://github.com/ecometrica/django-multisite
.. _django-tag-parser: https://github.com/edoburu/django-tag-parser
.. _django-taggit-autosuggest: https://bitbucket.org/fabian/django-taggit-autosuggest
.. _django-threadedcomments: https://github.com/HonzaKral/django-threadedcomments.git
.. _django-wysiwyg: https://github.com/pydanny/django-wysiwyg
.. _micawber: https://github.com/coleifer/micawber
.. _SoundCloud: https://soundcloud.com/
.. _noembed: http://noembed.com/
.. _`Speaker Desk`: https://speakerdeck.com/
