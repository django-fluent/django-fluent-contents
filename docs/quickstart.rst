.. _quickstart:

Quick start guide
=================

Installing django-fluent-contents
---------------------------------

The base installation of django-fluent-contents requires Django version 1.3 or higher and `django-polymorphic` 0.2 or higher.

The package can be installed with the following commands::

    cd django-fluent-contents
    python setup.py install .

The additional plugins may add additional requirements; the plugins will warn about then when they are used for the first time.
For optional dependency management, it is strongly recommended that you run the application inside a `virtualenv`.


Basic setup
-----------

Next, create a project which uses the module.
The basic module can be installed and optional plugins can be added:

.. code-block:: python

    INSTALLED_APPS += (
        'fluent_contents',
        'django_wysiwyg',

        # And optionally add the desired plugins:
        'fluent_contents.plugins.text',                # requires django-wysiwyg
        'fluent_contents.plugins.code',                # requires pygments
        'fluent_contents.plugins.gist',
        'fluent_contents.plugins.googledocsviewer',
        'fluent_contents.plugins.iframe',
        'fluent_contents.plugins.markup',
        'fluent_contents.plugins.rawhtml',
    )

Since some extra plugins are used here, make sure their applications are installed::

    pip install django-wysiwyg pygments


.. note::

    Each plugin is optional. Only the ``fluent_contents`` application is required, allowing to write custom models and plugins.
    Since a layout with the :ref:`text <text>` and :ref:`code <code>` plugin form a good introduction, these are added here.

Afterwards, you can setup the database::

    ./manage.py syncdb


Displaying content
------------------

Finally, it needs a model or application that displays the content.
The most simply way, is adding a :class:`~fluent_contents.models.fields.PlaceholderField` to a model:

.. code-block:: python

    class Article(models.Model):
        title = models.CharField("Title", max_length=200)
        slug = models.SlugField("Slug", unique=True)
        content = PlaceholderField("article_content")

        class Meta:
            verbose_name = "Article"
            verbose_name_plural = "Articles"

        def __unicode__(self):
            return self.title


Make sure the admin screen uses either the :class:`~fluent_contents.admin.placeholderfield.PlaceholderFieldAdmin` or :class:`~fluent_contents.admin.placeholderfield.PlaceholderFieldAdminMixin` class.
This makes sure additional inlines are added the the admin screen:

.. code-block:: python

    class ArticleAdmin(PlaceholderFieldAdmin):
        pass

    admin.site.register(Article, ArticleAdmin)

No extra configuration is required, the field will simply blend in with the rest of the form fields.
Gven that the article is displayed by a template (i.e. ``article/details.html``)
it can use the ``placeholder_tags`` to display the contents:

.. code-block:: html+django

    {% load placeholder_tags %}
    {% render_placeholder article.content %}

That's it!


Optional features
-----------------

To add even more plugins, use::

    INSTALLED_APPS += (
        'fluent_contents',

        # Dependencies for plugins:
        'disqus',
        'django.contrib.comments',
        'django_wysiwyg',
        'form_designer',

        # All plugins:
        'fluent_contents.plugins.text',                # requires django-wysiwyg
        'fluent_contents.plugins.code',                # requires pygments
        'fluent_contents.plugins.gist',
        'fluent_contents.plugins.googledocsviewer',
        'fluent_contents.plugins.iframe',
        'fluent_contents.plugins.markup',
        'fluent_contents.plugins.rawhtml',

        'fluent_contents.plugins.commentsarea',        # requires django.contrib.comments + templates
        'fluent_contents.plugins.disquswidgets',       # requires django-disqus + DISQUS_API_KEY
        'fluent_contents.plugins.formdesignerlink',    # requires django-form-designer from github.
    )

    DISQUS_API_KEY = '...'
    DISQUS_WEBSITE_SHORTNAME = '...'

    FLUENT_MARKUP_LANGUAGE = 'reStructuredText'        # can also be markdown or textile

Most of the features are glue to existing Python or Django modules,
hence these packages need to be installed:

* ``django_wysiwyg`` (for the :ref:`text <text>` plugin)
* ``Pygments`` (for the :ref:`code <code>` plugin)
* ``docutils`` (for the :ref:`markup <markup>` plugin)
* ``django-disqus`` (for the :ref:`disquscommentsarea <disquscommentsarea>` plugin)
* `django-form-designer <http://github.com/philomat/django-form-designer>` (for the :ref:`formdesignerlink <formdesignerlink>` plugin)

The reason all these features are optional is make them easily swappable for other implementations.
You can use a different comments module, or invert new content plugins.
It makes the CMS configurable in the way that you see fit.

Some plugins, like the commentsarea from `django.contrib.comments`, might make a bad first impression
because they have no default layout. This turns out however, to make them highly adaptable
to your design and requirements.


Creating a CMS system:
----------------------

The django-fluent-contents package also offers a :class:`~fluent_contents.admin.placeholdereditor.PlaceholderEditorAdmin` class
and :class:`~fluent_contents.admin.placeholdereditor.PlaceholderEditorAdminMixin` mixin which allows CMS-developers
to display the content plugins at various locations of a CMS page.
For more information, see the :doc:`cms`.

Testing your new shiny project
------------------------------

Congrats! At this point you should have a working installation.
Now you can just login to your admin site and see what changed.

