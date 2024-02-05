Changelog
=========

Changes in 3.1 (2024-02-05)
---------------------------

* Fixed Django 4 admin styling issues.
* Fixed deprecation warnings.
* Removed left-over Django 2.1 compatibility code.


Changes in 3.0 (2021-11-17)
---------------------------

* Added Django 4 compatibility.
* Fixed OEmbed maxwidth/maxheight parameters.
* Fixed using request as positional arg in ``PlaceholderFieldAdmin.formfield_for_dbfield()``.
* Fixed unneeded warnings from ``placeholder_tags`` usage.
* Fixed keeping a lock unneededly when app loading was complete.
* Fixed ``HttpRedirectRequest`` to operate on a lazy value.
* Replaced Travis with GitHub actions.
* Dropped Python 2.7 support.
* Dropped Django 1.11, 2.0, 2.1 support.


Changes in 2.0.7 (2020-01-04)
-----------------------------

* Fix Django 3.0 compatibility by removing ``curry()`` call.
* Bump setup requirements to ensure Django 3.0 compatibility.


Changes in 2.0.6 (2019-06-11)
-----------------------------

* Fix Django 2.x compatibility with ``disquswidgets`` and ``formdesignerlink`` migrations.
* Fix Python error when adding a ``ContentItem`` on a parent model that doesn't have a ``parent_site`` field.
* Replace *django-form-designer* GitHub dependency with updated django-form-designer-ai_ PyPI release.
* Reformat all files with isort, black and prettier.


Changes in 2.0.5 (2019-04-12)
-----------------------------

* Fixed compatibility with Django 2.2


Changes in 2.0.4 (2018-08-27)
-----------------------------

* Fixed showing languages in the copy button which are not part of ``PARLER_LANGUAGES``.
* Fixed storing ``MarkupItem`` under it's proxy class type ID.
* Fixed missing return value from ``CachedModelMixin.delete()``.
* Fixed reading ``context.request`` for content plugin templates.
* Fixed including ``cp_tabs.js`` in ``PlaceholderFieldAdmin``.
* Fixed HTML comment output escaping for missing database tables.
* Fixed errors in ``get_plugins_by_name()`` when object instances are passed.
* Fixed ``Placeholder.DoesNotExist`` warning to display proper ContentType ID for proxy models.
* Fixed leaving empty ``.form-row`` elements in the admin page.
* Fixed ``start_content_plugin`` command, template was missing in ``MANIFEST``.
* Fixed Python 3 support for ``Placeholder.__repr__()``.


Changes in 2.0.3 (2018-05-14)
-----------------------------

* Fixed twitter-text extra requires dependency for Python 3 support
  Use ``twitter-text`` instead of the outdated ``twitter-text-py``.


Changes in 2.0.2 (2018-02-12)
-----------------------------

* Fixed JavaScript media file ordering for Django 2.0


Changes in 2.0.1 (2018-02-05)
-----------------------------

* Added ``Meta.manager_inheritance_from_future = True`` to all ``ContentItem`` subclasses that
  define a ``Meta`` class. This avoids warnings in the latest django-polymorphic_ 2.0.1 release.
  It also makes sure all sub-sub classes are correctly fetched (an unlikely use-case though).
* Fixed deprecation warnings for Django 2.1
* Fixed setup classifiers


Changes in 2.0 (2018-01-22)
---------------------------

* Added Django 2.0 support.
* Removed compatibility with very old ``django-form-designer`` versions.
* Dropped Django 1.7, 1.8, 1.9 support.


Changes in 1.2.2 (2017-11-22)
-----------------------------

* Fixed compatibility with upcoming django-polymorphic_ release.
* Delayed twittertext plugin checks.
* Removed unneeded ``fluent_utils.django_compat`` imports.


Changes in 1.2.1 (2017-08-10)
-----------------------------

* Fixed Django 1.10+ wanting to create new migrations.
* Fixed inconsistent ordering of "markup item" language choices.
* Fixed str/bytes differences in migrations between Python 2 and 3.


Changes in 1.2 (2017-05-01)
---------------------------

* Django 1.11 support.
* Fixd garbled placeholder data in admin forms submitted with errors
* Fixed JavaScript ``django_wysiwyg`` error when text plugin is not included.
* Dropped Django 1.5, 1.6 and Python 2.6 support.


Changes in 1.1.11 (2016-12-21)
------------------------------

* Fixed "Copy language" button for Django 1.10+
* Fix slot parameter for tests ``fluent_contents.tests.factories.create_placeholder()``


Changes in 1.1.10 (2016-12-15)
------------------------------

* Fixed "Copy language" button for Django 1.9+


Changes in 1.1.9 (2016-12-06)
-----------------------------

* Added ``find_contentitem_urls`` management command to index URL usage.
* Added ``remove_stale_contentitems --remove-unreferenced`` option to remove
  content items that no longer point to an existing page.
* Make sure the OEmbed plugin generates links with ``https://`` when
  ``SECURE_SSL_REDIRECT`` is set, or ``FLUENT_OEMBED_FORCE_HTTPS`` is enabled.
* Fixed loosing jQuery event bindings in the admin.


Changes in 1.1.8 (2016-11-09)
-----------------------------

* Added ``remove_stale_contentitems`` command for cleaning unused ``ContentItem`` objects.
  This also allows the migrations to remove the stale ``ContentType`` models afterwards.
* Fixed ``start_content_plugin`` command for Django 1.7
* Fixed ``MiddlewareMixin`` usage for Django 1.10 middleware support
* Fixed ``is_template_updated()`` check for some Django 1.8 template setups.


Changes in 1.1.7 (2016-10-05)
-----------------------------

* Added animations when moving content items, using the up/down buttons.
* Added drag&drop support on the title bar for reordering content items.

Although new feature additions usually mandate a new point release ("1.2'), these two
improvements are too wonderful to delay further. Hence they are backported from development.


Changes in 1.1.6 (2016-09-11)
-----------------------------

* Added ``start_content_plugin`` management command.
* Fixed running `clear_cache()` too early on a new model; it executed before saving/retrieving a primary key.
* Fixed unwanted HTML escaping for output comments that report stale models.
* Fixed Python errors during debugging when the debug toolbar panel finds stale models.
* Fixed errors by ``context.flatten()`` on plugin rendering (e.g. when using *django-crispy-forms*).
* Fixed ``ContentPlugin.ADMIN_TEMPLATE_WITHOUT_LABELS`` template when displaying multiple fields on a single line.


Changes in 1.1.5 (2016-08-06)
-----------------------------

* Fixed usage of deprecated ``context_instance`` for Django 1.10 compatibility.
* Fixed delete dialog in the Django admin when the page has stale context items.
* Fixed compatibility with html5lib 0.99999999/1.0b9

**BACKWARDS INCOMPATIBLE:** the custom merging template that's used in ``{% page_placeholder  .. template=".." %}``
no longer receives any custom context processor data defined in ``context_processors`` / ``TEMPLATE_CONTEXT_PROCESSORS``.
Only the standard Django context processors are included (via the ``PluginContext``).
The standard template values like ``{{ request }}``, ``{{ STATIC_URL }}`` and ``{% csrf_token %}`` still work.


Changes in 1.1.4 (2016-05-16)
-----------------------------

* Added ``fluent_contents.tests.factories`` methods for easier plugin testing.
* Added missing django-fluent-comments_ media files for ``contentarea`` plugin.
  This is configurable with the ``FLUENT_COMMENTSAREA_INCLUDE_STATIC_FILES`` setting,
  that defaults to ``FLUENT_BLOGS_INCLUDE_STATIC_FILES`` (``True``).
* Fixed appearance in django-flat-theme / Django 1.9.
* Fixed proxy model support for ``ContentItem`` models.
* Fixed Markup plugin rendering.
* Fixed reStructuredText rendering, avoid rendering the whole HTML document.


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
.. _django-debug-toolbar: https://github.com/jazzband/django-debug-toolbar
.. _django-flat-theme: https://github.com/elky/django-flat-theme
.. _django-fluent-comments: https://github.com/django-fluent/django-fluent/comments
.. _django-form-designer-ai: https://github.com/andersinno/django-form-designer-ai
.. _django-parler: https://github.com/edoburu/django-parler
.. _django-polymorphic: https://github.com/django-polymorphic/django-polymorphic
.. _django-multisite: https://github.com/ecometrica/django-multisite
.. _django-tag-parser: https://github.com/edoburu/django-tag-parser
.. _django-taggit-autosuggest: https://bitbucket.org/fabian/django-taggit-autosuggest
.. _django-threadedcomments: https://github.com/HonzaKral/django-threadedcomments.git
.. _django-wysiwyg: https://github.com/pydanny/django-wysiwyg
.. _micawber: https://github.com/coleifer/micawber
.. _SoundCloud: https://soundcloud.com/
.. _noembed: http://noembed.com/
.. _`Speaker Desk`: https://speakerdeck.com/
