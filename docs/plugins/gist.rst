.. _gist:

The gist plugin
===============

The `gist` plugin provides highlighting of programming code snippets (referred to as `Gists <https://gist.github.com/>`_),
which are hosted at `GitHub <http://www.github.com/>`_.

Installation
------------

Add the following settings to ``settings.py``:

.. code-block:: python

    INSTALLED_APPS += (
        'fluent_contents.plugins.gist',
    )

The plugin does not provide additional configuration options, nor does it have dependencies on other packages.
