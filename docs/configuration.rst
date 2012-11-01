.. _configuration:

Configuration
=============

A quick overview of the available settings:

.. code-block:: python

    FLUENT_CONTENTS_CACHE_OUTPUT = True

.. _FLUENT_CONTENTS_CACHE_OUTPUT:

FLUENT_CONTENTS_CACHE_OUTPUT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, the output of all plugins is cached.
It only updates when a staff member saves saves changes in in the admin screen.
This greatly improves the performance of the web site, as very little database queries are needed,
and most pages look the same for every visitor anyways.

In case this conflicts with your caching setup,
you can disable this feature side-wide bu setting this to ``False``.
