.. _configuration:

Configuration
=============

A quick overview of the available settings:

.. code-block:: python

    FLUENT_CONTENTS_CACHE_OUTPUT = True

.. _FLUENT_CONTENTS_CACHE_OUTPUT:

FLUENT_CONTENTS_CACHE_OUTPUT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, the HTML output of all plugins is cached.
The output is only updated when a staff member saves changes in in the Django admin.
Caching greatly improves the performance of the web site, as very little database queries are needed.
Most pages look the same for every visitor anyways.

In case this conflicts with your caching setup,
disable this feature side-wide by setting this flag to ``False``.
