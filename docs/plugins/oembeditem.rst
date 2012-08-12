.. _oembeditem:

The oembeditem plugin
===========================

The `oembeditem` plugin allows inserting an embedded online content in the page,
such as a YouTube video, Slideshare presentation, Twitter status, Flickr photo, etc..

  .. image:: /images/plugins/oembeditem-admin.*
     :width: 957px
     :height: 166px

The presentation is rendered with the embed code:

  .. image:: /images/plugins/oembeditem-html.*
     :width: 430px
     :height: 384px

By default, the following services are supported:

* `Blip.tv <http://blip.tv/>`_
* `DailyMotion <http://www.dailymotion.com/>`_
* `Flickr <http://www.flickr.com/>`_  (both videos and images)
* `FunnyOrDie <http://www.funnyordie.com/>`_
* `GitHub Gists <https://gist.github.com/>`_
* `Hulu <http://www.hulu.com/>`_
* `Mobypicture <http://www.mobypicture.com/>`_
* `Photobucket <http://photobucket.com/>`_
* `Polldaddy <http://polldaddy.com/>`_
* `Qik <http://qik.com/>`_
* `Revision3 <http://revision3.com/>`_
* `Scribd <http://www.scribd.com/>`_
* `Slideshare <http://www.slideshare.net/>`_
* `SmugMug <http://www.smugmug.com/>`_
* `Twitter <http://twitter.com/>`_ (status messages)
* `Viddler <http://www.viddler.com/>`_
* `Vimeo <http://vimeo.com/>`_
* `Wordpress.tv <http://wordpress.tv/>`_
* `yfrog <http://yfrog.com/>`_
* `YouTube <http://www.youtube.com/>`_  (public videos and playlists)

By using the paid `embed.ly`_ service, many other sites are supported.


Installation
------------

Add the following settings to ``settings.py``:

.. code-block:: python

    INSTALLED_APPS += (
        'fluent_contents.plugins.oembeditem',
    )

The dependencies can be installed via `pip`::

    pip install micawber


Configuration
-------------

The following settings are available:

.. code-block:: python

    FLUENT_OEMBED_SOURCE = 'list'   # "list", "basic" or "embedly"

    FLUENT_OEMBED_PROVIDER_LIST = (
        (r'http://(www\.)?youtube\.com/watch\S*',  'http://www.youtube.com/oembed'),
        (r'http://youtu\.be/\S*',                  'http://www.youtube.com/oembed'),
        (r'http://blip\.tv/\S*',                   'http://blip.tv/oembed/'),
        (r'http://(www\.)?vimeo\.com/\S*',         'http://vimeo.com/api/oembed.json'),

        # ...
    )

    FLUENT_OEMBED_PROVIDER_LIST_EXTRA = (

    )

    MICAWBER_EMBEDLY_KEY = ''


FLUENT_OEMBED_SOURCE
~~~~~~~~~~~~~~~~~~~~

The source to use for the OEmbed provider list. This can be one the following values:

* **list** Use the provides defined in ``FLUENT_OEMBED_PROVIDER_LIST``.
* **basic** Use the basic list defined in the micawber_ package.
* **embedly** Use the embed service from `embed.ly`_

The `embed.ly`_ service contains many providers, including sites which do not have an OEmbed implementation themselves.
The service does cost money, and requires an API key. For a list of providers supported by `embed.ly`_ see http://embed.ly/providers

The *list* setting is the default, and contains the services known to provide an OEmbed endpoint.


FLUENT_OEMBED_PROVIDER_LIST
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A fixed hard-coded list of providers.
Specify this setting to override the complete set of default OEmbed providers.
To add custom providers to the existing list, use ``FLUENT_OEMBED_PROVIDER_LIST_EXTRA`` instead.

Each item is a tuple with two fields:

* The regular expression to match the URL.
* The OEmbed provider endpoint.

Note that the regular expressions never test for ``.*`` but use ``\S*`` instead
so *micawber* can also detect the URL within a larger fragment.


FLUENT_OEMBED_PROVIDER_LIST_EXTRA
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The OEmbed providers in this setting will be added to the default ``FLUENT_OEMBED_PROVIDER_LIST`` value.
Each item is a tuple with the regular expression and endpoint URL.


MICAWBER_EMBEDLY_KEY
~~~~~~~~~~~~~~~~~~~~

The key to access the `embed.ly`_ service.


Security considerations
-----------------------

Note that an OEmbed element is fetched from another server, which specifies how the embed code looks like.
Hence, only known online services are whitelisted via the ``FLUENT_OEMBED_PROVIDER_LIST`` setting.
This reduces the risks for Cross-site scripting (XSS) attacks.

Hence, the OEmbed discovery protocol is not supported either.


.. _embed.ly: http://embed.ly/
.. _micawber: https://github.com/coleifer/micawber/
