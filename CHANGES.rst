Version 0.8.5 (in development)
------------------------------

* Added support for shared content.
* Fix *code* plugin compatibility with Pygments 1.6rc1.
* Fix escaping slot name in templates
* Bump version of django-wysiwyg_ to 0.5.1 because it fixes TinyMCE integration.


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


.. _django-threadedcomments: https://github.com/HonzaKral/django-threadedcomments.git
.. _django-wysiwyg: https://github.com/pydanny/django-wysiwyg

