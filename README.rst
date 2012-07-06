Introduction
============

The *fluent_contents* module offers a widget engine to display various content on a Django page.

This engine operates similary like Django CMS, FeinCMS or django-portlets,
however, it can be used for any project, or CMS system.

Available default content types:

**Standard content:**

* Text content - write rich text in a WYSIWYG editor (provided by django-wysiwyg_).
* Markup - write content with reStructuredText, Markdown or Textile (provided by *docutils*, *Markdown* or *textile*).
* Forms - display forms created with django-form-designer_.

**Online services:**

* Google Docs viewer - display a PDF or DOCX file on a page, using the Google Docs Viewer service.
* Twitter feed - display a Twitter timeline, or realtime search timeline.

**For programmers:**

* Code - display code snippets with highlighting (provided by *Pygments*).
* Gist - display Gist snippets from Github.
* IFrame - display an ``<iframe>`` on the page.
* Raw HTML content - include jQuery snippets, or "embed codes" by Google Docs, YouTube, Vimeo or SlideShare.

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

First install the module, preferably in a virtual environment. It can be installed from PyPI::

    pip install django-fluent-contents

Or the current folder can be installed::

    pip install .

Configuration
-------------

Next, create a project which uses the module::

    cd ..
    django-admin.py startproject fluentdemo

It should have the following settings::

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

The database tables can be created afterwards::

    ./manage.py syncdb

Finally, it needs a model or application that displays the content.
There are two ways to include content. The most simply way, is
adding a ``PlaceholderField`` to a model::

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

