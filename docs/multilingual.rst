Multilingual support
====================

.. versionadded:: 1.0

*django-fluent-contents* supports creating page content in multiple languages.
As all content items are added to a "parent" object, some support on the parent side is needed to use this feature.
The benefit however, is that you can use *django-fluent-contents* with any multilingual package.


Installation
------------

All created content items have a :attr:`~fluent_contents.models.ContentItem.language_code` attribute,
to identify the language an item was created in. This attribute is filled using the language of the parent
object those content items are created for.

The current language can be detected by providing:

* A :func:`get_current_language` method on the parent object.
  This covers all models that use django-parler_ for translation support.
* A :attr:`language_code` attribute or property on the parent object.

When such properly is found on the parent, all rendering functions use that information too.
For example, only content items that match the parent's language will be rendered.


Rendering items
---------------

Django projects can use a different language per request or URL, using any of these methods:

* Running a second instance with a different :django:setting:`LANGUAGE_CODE` setting.
* Using :class:`~django.middleware.locale.LocaleMiddleware` in combination with :func:`~django.conf.urls.i18n.i18n_patterns`.
* Writing code that calls :func:`translation.activate() <django.utils.translation.activate>` directly.

By default, all content items are rendered in the language they are created in.
When you switch the language, the item will still appear in the original language.
It uses :func:`translation.override <django.utils.translation.override>` during the rendering.

Without such strict policy, you risk combining database content of the original language,
and ``{% trans ".." %}`` content in the current language.
The output would become a mix of languages, and even be stored in the cache this way.

When you deal with this explicitly, this behavior can be disabled.
There are some plugin settings available:

* :attr:`~fluent_contents.extensions.ContentPlugin.cache_output_per_language` -
  Cache each rendering in the currently active language.
  This is perfect for using ``{% trans ".." %}`` tags in the template and items rendered in fallback languages too.
* :attr:`~fluent_contents.extensions.ContentPlugin.render_ignore_item_language` -
  Don't change the language at all. This is typically desired when
  :attr:`~fluent_contents.extensions.ContentPlugin.cache_output` is completely disabled.
  The :func:`~django.utils.translation.get_language` points to the active site language.

Fallback languages
------------------

When a page is not translated, the system can be instructed to render the fallback language.
The fallback language has to be defined in :ref:`FLUENT_CONTENTS_DEFAULT_LANGUAGE_CODE`.

In the templates, use:

.. code-block:: html+django

    {% render_placeholder ... fallback=True %}

The :func:`~fluent_contents.rendering.render_placeholder` function also has a ``fallback_language`` parameter.

.. _django-parler: https://github.com/edoburu/django-parler
