django-fluent-contents
======================

.. image:: https://img.shields.io/travis/edoburu/django-fluent-contents/master.svg?branch=master
    :target: http://travis-ci.org/edoburu/django-fluent-contents
.. image:: https://img.shields.io/pypi/v/django-fluent-contents.svg
    :target: https://pypi.python.org/pypi/django-fluent-contents/
.. image:: https://img.shields.io/pypi/dm/django-fluent-contents.svg
    :target: https://pypi.python.org/pypi/django-fluent-contents/
.. image:: https://img.shields.io/badge/wheel-yes-green.svg
    :target: https://pypi.python.org/pypi/django-fluent-contents/
.. image:: https://img.shields.io/pypi/l/django-fluent-contents.svg
    :target: https://pypi.python.org/pypi/django-fluent-contents/
.. image:: https://img.shields.io/codecov/c/github/edoburu/django-fluent-contents/master.svg
    :target: https://codecov.io/github/edoburu/django-fluent-contents?branch=master

The *fluent_contents* module offers a widget engine to display various content on a Django page.

This engine operates similarly like Django CMS, FeinCMS, Wagtail's streaming field or django-portlets,
however, it can be used for any project, or CMS system.

Page contents can be constructed with multiple "content items".
You can define your own content items, or use one the available content items out of the box.
Standard web sites could use the bundled default content items.
Other advanced designs (such as a web site with a magazine-like design, having many blocks at a page)
can be implemented quickly by defining content items for the various "style elements" at the page.

Web editors are able to place the "content items" at the page,
hence they can fill the content of advanced layouts easily and directly in the Django admin.
This also applies to pages which have a "free form" or "presentation slide" design,
this module allows the end-user to manage and configure the designed elements at the page.

By default, the following content items are available:

**Standard content:**

* Text content - write rich text in a WYSIWYG editor (provided by django-wysiwyg_).
* Markup - write content with reStructuredText, Markdown or Textile (provided by *docutils*, *Markdown* or *textile*).
* Forms - display forms created with django-form-designer_.

**Online content:**

* Google Docs viewer - display a PDF or DOCX file on a page, using the Google Docs Viewer service.
* OEmbed support - embed content from YouTube, Vimeo, SlideShare, Twitter, and more.
* Twitter feed - display a Twitter timeline, or realtime search timeline.

**For programmers:**

* Code - display code snippets with highlighting (provided by *Pygments*).
* Gist - display Gist snippets from Github.
* IFrame - display an ``<iframe>`` on the page.
* Raw HTML content - include jQuery snippets, or "embed codes" by other services.
* Shared content - display a set of items at multiple locations.

**Interactive:**

* Commentsarea - display comments on a page (provided by django.contrib.comments_).
* Disqusarea - display DISQUS comments on a page (provided by django-disqus_).
* Form-designer link - display a django-form-designer_ form on a page.

For more details, see the documentation_ at Read The Docs.


Screenshot
==========

The ``PlaceholderField`` is nicely integrated in the Django admin interface:

.. image:: https://github.com/edoburu/django-fluent-contents/raw/master/docs/images/admin/placeholderfieldadmin2.png
   :width: 770px
   :height: 562px
   :alt: django-fluent-contents placeholder field preview

Secondly, it's possible to build a CMS Page interface with the ``PlaceholderEditorAdmin``,
which displays each content placeholder in a tab:

.. image:: https://github.com/edoburu/django-fluent-contents/raw/master/docs/images/admin/placeholdereditoradmin1.png
   :width: 770px
   :height: 362px
   :alt: django-fluent-contents placeholder editor preview


Installation
============

First install the module, preferably in a virtual environment. It can be installed from PyPI:

.. code-block:: bash

    pip install django-fluent-contents

Or the current folder can be installed:

.. code-block:: bash

    pip install .

The dependencies of plugins are not included by default. To install those, include the plugin names as extra option:

.. code-block:: bash

    pip install django-fluent-contents[code,disquscommentsarea,formdesignerlink,markup,oembeditem,text,twitterfeed]

Configuration
-------------

Next, create a project which uses the module:

.. code-block:: bash

    cd ..
    django-admin.py startproject fluentdemo

It should have the following settings:

.. code-block:: python

    INSTALLED_APPS += (
        'fluent_contents',

        # And optionally all plugins desired:
        'fluent_contents.plugins.code',
        'fluent_contents.plugins.commentsarea',
        'fluent_contents.plugins.disquswidgets',
        'fluent_contents.plugins.formdesignerlink',
        'fluent_contents.plugins.gist',
        'fluent_contents.plugins.googledocsviewer',
        'fluent_contents.plugins.iframe',
        'fluent_contents.plugins.markup',
        'fluent_contents.plugins.rawhtml',
        'fluent_contents.plugins.text',

        # Some plugins need extra Django applications
        'disqus',
        'django.contrib.comments',
        'django_wysiwyg',
        'form_designer',
    )

The database tables can be created afterwards:

.. code-block:: bash

    ./manage.py migrate

Finally, it needs a model or application that displays the content.
There are two ways to include content. The most simply way, is
adding a ``PlaceholderField`` to a model:

.. code-block:: python

    # models.py:

    class Article(models.Model):
        title = models.CharField("Title", max_length=200)
        slug = models.SlugField("Slug", unique=True)
        content = PlaceholderField("article_content")

        class Meta:
            verbose_name = "Article"
            verbose_name_plural = "Articles"

        def __unicode__(self):
            return self.title


    # admin.py:

    class ArticleAdmin(PlaceholderFieldAdmin):
        pass

    admin.site.register(Article, ArticleAdmin)

The most advanced combination, is using the ``PlaceholderEditorAdmin`` or ``PlaceholderEditorAdminMixin`` classes.
These classes are designed for CMS-style applications which multiple placeholders on a page.
See the provided ``example`` application for details.

NOTE:

    The django-fluent-pages_ application is built on top of this API, and provides a ready-to-use CMS that can be implemented with minimal configuration effort.
    To build a custom CMS, the API documentation of the fluent_contents.admin_ module provides more details of the classes.

Details about the various settings are explained in the documentation_.


Creating custom content items
-----------------------------

To implement custom elements of a design - while making them editable for admins -
this module allows you to create custom content items.
Take a look in the existing types at ``fluent_contents.plugins`` to see how it's being done.

It boils down to creating a package with 2 files:

The ``models.py`` file should define the fields of the content item:

.. code-block:: python

  from django.db import models
  from fluent_contents.models import ContentItem

  class AnnouncementBlockItem(ContentItem):
      title = models.CharField("Title", max_length=200)
      body = models.TextField("Body")
      button_text = models.CharField("Text", max_length=200)
      button_link = models.URLField("URL")

      class Meta:
          verbose_name = "Announcement block"
          verbose_name_plural = "Announcement blocks"

      def __unicode__(self):
          return self.title

The ``content_plugins.py`` file defines the metadata and rendering:

.. code-block:: python

  from fluent_contents.extensions import plugin_pool, ContentPlugin
  from .models import AnnouncementBlockItem

  @plugin_pool.register
  class AnnouncementBlockPlugin(ContentPlugin):
     model = AnnouncementBlockItem
     render_template = "plugins/announcementblock.html"
     category = "Simple blocks"

The plugin can also define the admin layout, by adding fields such as a ``fieldset``, but that is all optional.
The template could look like:

.. code-block:: html+django

    <div class="announcement">
        <h3>{{ instance.title }}</h3>
        <div class="text">
            {{ instance.body|linebreaks }}
        </div>
        <p class="button"><a href="{{ instance.button_url }}">{{ instance.button_text }}</a></p>
    </div>

Et, voila: web editors are now able to place an announcement items at the page
in a very structured manner! Other content items can be created in the same way,
either in the same Django application, or in a separate application.


Contributing
------------

This module is designed to be generic. In case there is anything you didn't like about it,
or think it's not flexible enough, please let us know. We'd love to improve it!

If you have any other valuable contribution, suggestion or idea,
please let us know as well because we will look into it.
Pull requests are welcome too. :-)


.. _documentation: http://django-fluent-contents.readthedocs.org/
.. _fluent_contents.admin: http://django-fluent-contents.readthedocs.org/en/latest/cms.html

.. _django.contrib.comments: https://docs.djangoproject.com/en/dev/ref/contrib/comments/
.. _django-disqus: https://github.com/arthurk/django-disqus
.. _django-fluent-comments: https://github.com/edoburu/django-fluent-comments
.. _django-fluent-pages: https://github.com/edoburu/django-fluent-pages
.. _django-form-designer: https://github.com/philomat/django-form-designer.git
.. _django-polymorphic: https://github.com/chrisglass/django_polymorphic
.. _django-wysiwyg: https://github.com/pydanny/django-wysiwyg

