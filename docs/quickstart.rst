.. _quickstart:

Quick start guide
=================

Installing django-fluent-contents
---------------------------------

The base installation of django-fluent-contents requires Django version 1.3 or higher and django-polymorphic_ 0.2 or higher.

The package can be installed using::

    pip install django-fluent-contents

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

    pip install django-fluent-contents[text,code]


.. note::

    Each plugin is optional. Only the ``fluent_contents`` application is required, allowing to write custom models and plugins.
    Since a layout with the :ref:`text <text>` and :ref:`code <code>` plugin form a good introduction, these are added here.

Afterwards, you can setup the database::

    ./manage.py syncdb


Displaying content
------------------

Finally, it needs a model or application that displays the content.
The most simply way, is adding a :class:`~fluent_contents.models.PlaceholderField` to a model:

.. code-block:: python

    class Article(models.Model):
        title = models.CharField("Title", max_length=200)
        content = PlaceholderField("article_content")

        class Meta:
            verbose_name = "Article"
            verbose_name_plural = "Articles"

        def __unicode__(self):
            return self.title


Make sure the admin screen the :class:`~fluent_contents.admin.PlaceholderFieldAdmin` class.
This makes sure additional inlines are added the the admin screen:

.. code-block:: python

    class ArticleAdmin(PlaceholderFieldAdmin):
        pass

    admin.site.register(Article, ArticleAdmin)

No extra configuration is required, the field will simply blend in with the rest of the form fields.
Gven that the article is displayed by a template (i.e. ``article/details.html``)
it can use the ``fluent_contents_tags`` to display the contents:

.. code-block:: html+django

    {% load fluent_contents_tags %}
    {% render_placeholder article.content %}

That's it!


Fieldset layout
---------------

With a small change in the ``fieldsets`` configuration, the admin interface could look like this:

    .. image:: /images/admin/placeholderfieldadmin1.png
       :width: 770px
       :height: 562px
       :alt: django-fluent-contents placeholder field preview

When the placeholder is used in a separate ``fieldset`` that has a ``plugin-holder`` class name,
the field will be displayed without a label in front of it:

.. code-block:: python

    class ArticleAdmin(PlaceholderFieldAdmin):
        prepopulated_fields = {'slug': ('title',)}

        fieldsets = (
            (None, {
                'fields': ('title', 'slug'),
            }),
            ("Contents", {
                'fields': ('content',),
                'classes': ('plugin-holder',),
            })
        )

|

    .. image:: /images/admin/placeholderfieldadmin2.png
       :width: 770px
       :height: 562px
       :alt: django-fluent-contents placeholder field preview


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
        'fluent_contents.plugins.formdesignerlink',    # requires django-form-designer-ai
    )

    DISQUS_API_KEY = '...'
    DISQUS_WEBSITE_SHORTNAME = '...'

    FLUENT_MARKUP_LANGUAGE = 'reStructuredText'        # can also be markdown or textile

Most of the features are glue to existing Python or Django modules,
hence these packages need to be installed:

* django-wysiwyg_ (for the :ref:`text <text>` plugin)
* Pygments_ (for the :ref:`code <code>` plugin)
* docutils_ (for the :ref:`markup <markup>` plugin)
* django-disqus_ (for the :ref:`disquscommentsarea <disquscommentsarea>` plugin)
* `django-form-designer-ai`_ (for the :ref:`formdesignerlink <formdesignerlink>` plugin)

They can be installed using::

    pip install django-fluent-contents[text,code,markup,disquscommentsarea,formdesignerlink]

The reason that all these features are optional is make them easily swappable for other implementations.
You can use a different comments module, or invert new content plugins.
It makes the CMS configurable in the way that you see fit.

Some plugins, like the :ref:`commentsarea <commentsarea>` based on `django.contrib.comments`_,
might make a bad first impression because they have no default layout.
This turns out however to be by design, to make them highly adaptable to your design and requirements.


Creating a CMS system
---------------------

The django-fluent-contents package also offers a :class:`~fluent_contents.admin.PlaceholderEditorAdmin` class
which allows CMS-developers to display the content plugins at various locations of a CMS page.
For more information, see the :doc:`cms`.

Testing your new shiny project
------------------------------

Congrats! At this point you should have a working installation.
Now you can just login to your admin site and see what changed.


Production notes
----------------

When deploying the project to production, enable the following setting::

    FLUENT_CONTENTS_CACHE_PLACEHOLDER_OUTPUT = True

This improves the performance of the :ref:`template tags<templatetags>`.


.. _docutils: http://docutils.sourceforge.net/
.. _django.contrib.comments: https://docs.djangoproject.com/en/dev/ref/contrib/comments/
.. _django-disqus: https://github.com/arthurk/django-disqus
.. _django-form-designer-ai: https://github.com/andersinno/django-form-designer-ai
.. _django-polymorphic: https://github.com/django-polymorphic/django-polymorphic
.. _django-wysiwyg: https://github.com/pydanny/django-wysiwyg/
.. _Pygments: http://pygments.org/
