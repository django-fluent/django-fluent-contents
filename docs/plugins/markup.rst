.. _markup:

The markup plugin
=================

The `markup` plugin provides support for lightweight "markup" languages, such as:

* **reStructuredText**: The syntax known for Python documentation.
* **Markdown**: The syntax known for GitHub and Stack Overflow comments (both do have a dialect/extended version)
* **Textile**: The syntax known for Redmine and partially used in Basecamp and Google+.

For technical savy users, this makes it easy to write pages in a consistent style,
or publish wiki/RST documentation online.

The plugin uses `django.contrib.markup <https://docs.djangoproject.com/en/dev/ref/contrib/markup/>`_ internally
to provide the translation of the markup to HTML, hence it supports any markup language that `django.contrib.markup` has a filter for.

Installation
------------

Add the following settings to ``settings.py``:

.. code-block:: python

    INSTALLED_APPS += (
        'fluent_contents.plugins.markup',
    )

    FLUENT_MARKUP_LANGUAGE = 'restructuredtext'

Depending on the choosen markup language, the required dependency needs to be installed using `pip`:

For **restructuredtext**, use::

    pip install docutils

For **markdown**, use::

    pip install Markdown

For **textile**, use::

    pip install textile

Configuration
-------------

The following settings are available:

.. code-block:: python

    FLUENT_MARKUP_LANGUAGE = 'restructuredtext'


FLUENT_MARKUP_LANGUAGE
~~~~~~~~~~~~~~~~~~~~~~

Define which markup language should be used.

The supported values are:

* *restructuredtext*
* *markdown*
* *textile*

The plugin currently assumes that only one type of language will be used;
that either the pages are written in reStructuredText, Markdown or Textile.
In case the language is switched, the existing plugin instances will remember
the markup language they were written in, and keep using that.

