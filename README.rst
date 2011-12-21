Introduction
============

The ``fluent_contents`` module offers a widget engine to display various content on a Django page.

This engine operates similary like Django CMS, FeinCMS or django-portlets,
however, it can be used for any project, or CMS system.

Available default content types:

* Standard content:

 * Text content - write rich text in a WYSIWYG editor (provided by `django-wysiwyg`).
 * Google Docs viewer - display a PDF or DOCX file on a page, using the Google Docs Viewer service.

* For programmers:

 * Code - display code snippets with highlighting (provided by `Pygments`).
 * Gist - display Gist snippets from Github.
 * IFrame - display an ``<iframe>`` on the page.
 * Raw HTML content - include jQuery snippets, or "embed codes" by Google Docs, YouTube, Vimeo or SlideShare.
 * Markup - write content with reStructuredText, Markdown or Textile (provided by `docutils`, `Markdown` or `textile`).

* Interactive:

 * Commentsarea - display comments on a page (provided by `django.contrib.comments`).
 * Disqusarea - display DISQUS comments on a page (provided by `django-disqus`).
 * Form-designer link - display a `django-form-designer` form on a page.


Screenshot
==========

TODO

Installation
============

First install the module, preferably in a virtual environment. It can be installed from PyPI::

    pip install django-fluent-contents

Or the current folder can be installed::

    pip install .

Configuration
-------------

Next, create a project which uses the CMS::

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
        'django_wysiwyg',
        'disqus',
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

Details about the various settings are explained in the documentation.

