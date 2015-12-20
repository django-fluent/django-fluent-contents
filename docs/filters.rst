HTML Text Filters
=================

Plugins that deal with HTML content, can opt-in to the filtering framework.
This helps to improve HTML output consistently everywhere.


Bundled filters
---------------

This package has a two standard filters included:

* :func:`fluent_contents.plugins.text.filters.smartypants.smartypants_filter`
  can be added to :ref:`FLUENT_TEXT_PRE_FILTERS` to replace regular quotes with curly quotes.
  It needs smartypants_ to be installed.
* :func:`fluent_contents.plugins.text.filters.softhypen.softhypen_filter`
  can be added to :ref:`FLUENT_TEXT_POST_FILTERS` to insert soft-hyphenation characters in the text ( ``&shy;`` as HTML entity).
  It needs django-softhyphen_ to be installed.


Filter types
------------

A filter may be included in one of these settings:

* Pre-filters are listed in :ref:`FLUENT_TEXT_PRE_FILTERS`
* Post-filters are listed in :ref:`FLUENT_TEXT_POST_FILTERS`

While some filters could be used in both settings, there is a semantic difference.

Pre-filters
~~~~~~~~~~~

Any changes made by pre-filters affect the original text. These changes are visible in the WYSIWYG editor after saving.
Thus, the pre-filter should be idempotent; it should be able to run multiple times over the same content.
Typical use cases of a pre-filter are:

* Validate HTML
* Sanitize HTML (using bleach_)
* Replace ``"``regular quotes``"`` with curly "smart" quotes.

Post-filters
~~~~~~~~~~~~

The changes made by post-filters are *not* stored in the original text, and won't be visible in the WYSIWYG editor.
This allows a free-form manipulation of the text, for example to:

* Add soft-hyphens in the code for better line breaking.
* Improve typography, such as avoiding text widows, highlighting ampersands, etc.. (using django-typogrify_).
* Highlight specific words.
* Parse "short codes" - if you really must do so.
  *Please consider short codes a last resort.* It's recommended to create new plugins instead for complex integrations.

Since post-filters never change the original text, any filter function can be safely included as post-filter.
When there is an unwanted side-effect, simply remove the post-filter and resave the text.

Creating filters
----------------

Each filter is a plain Python function that receives 2 parameters:

* The :class:`~fluent_contents.models.ContentItem` model, and
* The HTML text it can update.

For example, see the smartypants filter:

.. code-block:: python

    from smartypants import smartypants

    def smartypants_filter(contentitem, html):
        return smartypants(html)

Since the original :class:`~fluent_contents.models.ContentItem` model is provided,
a filter may read fields such as
:attr:`contentitem.language_code <fluent_contents.models.ContentItem.language_code>`,
:attr:`contentitem.placeholder <fluent_contents.models.ContentItem.placeholder>` or
:attr:`contentitem.parent <fluent_contents.models.ContentItem.parent>`
to have context.

The filters may also raise a :class:`~django.core.exceptions.ValidationError`
to report any errors in the text that should be corrected by the end-user.

Supporting filters in custom plugins
------------------------------------

The bundled :ref:`text plugin <text>` already uses the filters out of the box.
When creating a custom plugin that includes a HTML/WYSIWYG-field,
overwrite the :meth:`~django.db.models.Model.full_clean` method in the model:

.. code-block:: python

    from django.db import models
    from fluent_contents.extensions import PluginHtmlField
    from fluent_contents.models import ContentItem
    from fluent_contents.utils.filters import apply_filters


    class WysiwygItem(ContentItem):
        html = PluginHtmlField("Text")
        html_final = models.TextField(editable=False, blank=True, null=True)

        def full_clean(self, *args, **kwargs):
            super(TextItem, self).full_clean(*args, **kwargs)
            self.html, self.html_final = apply_filters(self, self.html, field_name='html')

The :class:`~fluent_contents.extensions.PluginHtmlField` already provides the standard
cleanup and sanitation checks that the :ref:`FLUENT_TEXT_CLEAN_HTML`
and :ref:`FLUENT_TEXT_SANITIZE_HTML` settings enable.


.. _bleach: https://github.com/mozilla/bleach
.. _django-softhyphen: https://github.com/datadesk/django-softhyphen/
.. _django-typogrify: https://github.com/chrisdrackett/django-typogrify
.. _smartypants: https://pypi.python.org/pypi/smartypants/
