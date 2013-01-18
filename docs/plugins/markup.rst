.. _markup:

The markup plugin
=================

The `markup` plugin provides support for lightweight "markup" languages.

  .. image:: /images/plugins/markup-admin.*
     :width: 732px
     :height: 191px

The markup language is rendered as HTML:

  .. image:: /images/plugins/markup-html.*
     :width: 690px
     :height: 190px

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

Install the dependencies via *pip*::

    pip install django-fluent-contents[markup]

Depending on the choosen markup language, the required dependencies can also installed separately using `pip`:

For **reStructuredText**, use::

    pip install docutils

For **Markdown**, use::

    pip install Markdown

For **Textile**, use::

    pip install textile

Add the following settings to ``settings.py``:

.. code-block:: python

    INSTALLED_APPS += (
        'fluent_contents.plugins.markup',
    )

    FLUENT_MARKUP_LANGUAGES = ['restructuredtext', 'markdown', 'textile']


Configuration
-------------

The following settings are available:

.. code-block:: python

    FLUENT_MARKUP_LANGUAGES = ['restructuredtext', 'markdown', 'textile']
    FLUENT_MARKUP_MARKDOWN_EXTRAS = ["extension1_name", "extension2_name", "..."]


FLUENT_MARKUP_LANGUAGES
~~~~~~~~~~~~~~~~~~~~~~~

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

