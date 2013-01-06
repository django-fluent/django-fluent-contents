In development
--------------

* Fix template name for django-threadedcomments_ to ``comment/list.html``,
  to be compatible with the pull request at https://github.com/HonzaKral/django-threadedcomments/pull/39.
* Use plugin dependencies installation via the optional dependency specifier (e.g. ``django-fluent-contents[text]``).


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

