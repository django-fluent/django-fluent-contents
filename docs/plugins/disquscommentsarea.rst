.. _disquscommentsarea:

The disquscommentsarea plugin
=============================

The `disquscommentsarea`  plugin displays a comments area powed by DISQUS_.

  .. image:: /images/plugins/disquscommentsarea-admin.*
     :width: 732px
     :height: 61px

This displays the DISQUS_ comments area:

  .. image:: /images/plugins/disquscommentsarea-html.*
     :width: 441px
     :height: 490px

In the background, DISQUS_ uses a JavaScript include to embed the comments.
Google indexes the comments nevertheless.

The plugin uses django-disqus_ internally to render the HTML output.
The django-disqus_ module also offers management commands
to import the comments of django.contrib.comments_ to DISQUS_,
or export the comments from DISQUS_ as JSON or WXR feed.


Installation
------------

Install the dependencies via *pip*::

    pip install django-fluent-contents[disquscommentsarea]

This installs django-disqus_.

Add the following settings to ``settings.py``:

.. code-block:: python

    INSTALLED_APPS += (
        'disqus',
        'fluent_contents.plugins.disquscommentsarea',
    )

    DISQUS_API_KEY = '..'     # Insert API key here.
    DISQUS_SHORTNAME = '..'   # Insert the website shortname.


Configuration
-------------

The plugin does not provide any additional configuration,
it fully relies on the templatetags of django-disqus_ to provide a proper comments area.

* The API key can be created at the DISQUS_ website.
  You can `get your API key here`_ (you must be logged in on the DISQUS_ website).
  To see the shortname of your website, navigate to Settings->General on the DISQUS_ website.

* Secondly, make sure the `django.contrib.sites` framework is configured,
  including the domain name where the pages should be displayed.

.. tip::

    While the DISQUS_ include provides all default styles, it can be useful to specify some default styling as well.
    This avoids any undesired minor jumps by page elements when DISQUS_ is loading.

.. _get your API key here: http://disqus.com/api/get_my_key/
.. _DISQUS: http://disqus.com
.. _django-disqus: https://github.com/arthurk/django-disqus
.. _django.contrib.comments: https://docs.djangoproject.com/en/dev/ref/contrib/comments/
