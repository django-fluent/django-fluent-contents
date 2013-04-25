Version 0.9
-------------

* Added ``FLUENT_CONTENTS_PLACEHOLDER_CONFIG`` variable to limit plugins in specific placeholder slots.
* Added model fields for plugin developers, to have a consistent interface.
  The model fields integrate with django-any-urlfield_, django-any-imagefield_ and django-wysiwyg_.
* Added picture plugin.


Version 0.8.6
-------------

* Fixed metaclass errors in markup plugin for Django 1.5 / six.
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
.. _django-polymorphic: https://github.com/chrisglass/django_polymorphic
.. _django-tag-parser: https://github.com/edoburu/django-tag-parser
.. _django-threadedcomments: https://github.com/HonzaKral/django-threadedcomments.git
.. _django-wysiwyg: https://github.com/pydanny/django-wysiwyg
.. _micawber: https://github.com/coleifer/micawber
.. _SoundCloud: https://soundcloud.com/
.. _noembed: http://noembed.com/
.. _`Speaker Desk`: https://speakerdeck.com/
