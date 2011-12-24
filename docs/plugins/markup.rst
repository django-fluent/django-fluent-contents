.. _markup:

The markup plugin
=================

The `markup` plugin provides support for lightweight "markup" languages.

.. image:: /images/plugins/markup-admin.*
   :width: 788px
   :height: 182px

.. image:: /images/plugins/markup-html.*
   :width: 398px
   :height: 202px

The plugin provided support for the markup languages:

* **reStructuredText**: The syntax known for Python documentation.
* **Markdown**: The syntax known for GitHub and Stack Overflow comments (both do have a dialect/extended version)
* **Textile**: The syntax known for Redmine and partially used in Basecamp and Google+.

For technical savy users, this makes it easy to write pages in a consistent style,
or publish wiki/RST documentation online.

The plugin uses django.contrib.markup_ internally to provide the translation of the markup to HTML,
hence it supports any markup language that django.contrib.markup_ has a filter for.

Installation
------------

Add the following settings to ``settings.py``:

.. code-block:: python

    INSTALLED_APPS += (
        'fluent_contents.plugins.markup',
    )

    FLUENT_MARKUP_LANGUAGES = ['restructuredtext', 'markdown', 'textile']

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


FLUENT_MARKUP_LANGUAGES
~~~~~~~~~~~~~~~~~~~~~~

Define which markup language should be used.

This is a list/tuple, which can contain the following values:

* *restructuredtext*
* *markdown*
* *textile*

By default, all languages are added.

FLUENT_MARKUP_MARKDOWN_EXTRAS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Define the markdown extensions to use.

.. _django.contrib.markup: https://docs.djangoproject.com/en/dev/ref/contrib/markup/

