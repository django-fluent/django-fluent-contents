.. _code:

The code plugin
===============

The `code` plugin provides highlighting for programming code.

  .. image:: /images/plugins/code-admin.*
     :width: 732px
     :height: 225px

The plugin uses Pygments_ as backend to perform the highlighting:

  .. image:: /images/plugins/code-html.*
     :width: 380px
     :height: 250px

The color theme can be configured in the settings.


Installation
------------

Install the dependencies via *pip*::

    pip install django-fluent-contents[code]

This installs the Pygments_ package.

Add the following settings to ``settings.py``:

.. code-block:: python

    INSTALLED_APPS += (
        'fluent_contents.plugins.code',
    )


Configuration
-------------

No settings have to be defined.
For further tuning however, the following settings are available:

.. code-block:: python

    FLUENT_CODE_DEFAULT_LANGUAGE = 'html'
    FLUENT_CODE_DEFAULT_LINE_NUMBERS = False

    FLUENT_CODE_STYLE = 'default'

    FLUENT_CODE_SHORTLIST = ('python', 'html', 'css', 'js')
    FLUENT_CODE_SHORTLIST_ONLY = False


FLUENT_CODE_DEFAULT_LANGUAGE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Define which programming language should be selected by default.

This setting is ideally suited to set personal preferences.
By default this is "HTML", to be as neutral as possible.


FLUENT_CODE_DEFAULT_LINE_NUMBERS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Define whether line number should be enabled by default for any new plugins.


FLUENT_CODE_STYLE
~~~~~~~~~~~~~~~~~

The desired highlighting style. This can be any of the themes that Pygments_ provides.

Each style name refers to a python module in the :mod:`pygments.styles` package.
The styles provided by Pygments_ 1.4 are:

* *autumn*
* *borland*
* *bw* (black-white)
* *colorful*
* *default*
* *emacs*
* *friendly*
* *fruity*
* *manni*
* *monokai*
* *murphy*
* *native*
* *pastie*
* *perldoc*
* *tango*
* *trac*
* *vim*
* *vs* (Visual Studio colors)


.. note::
    This setting cannot be updated per plugin instance, to avoid a mix of different styles used together.
    The entire site uses a single consistent style.


FLUENT_CODE_SHORTLIST
~~~~~~~~~~~~~~~~~~~~~

The plugin displays a shortlist of popular programming languages in the "Language" selectbox,
since Pygments provides highlighting support for many many programming languages.

This settings allows the shortlist to be customized.


FLUENT_CODE_SHORTLIST_ONLY
~~~~~~~~~~~~~~~~~~~~~~~~~~

Enable this setting to only show the programming languages of the shortlist.
This can be used to simplify the code plugin for end users.


.. _Pygments: http://pygments.org/
