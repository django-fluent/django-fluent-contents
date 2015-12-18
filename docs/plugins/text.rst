.. _text:

The text plugin
===============

The `text` plugin provides a standard WYSIWYG ("What You See is What You Get")
editor in the administration panel, to add HTML contents to the page.

.. image:: /images/plugins/text-admin.*
   :width: 732px
   :height: 269px

.. not needed: image:: /images/plugins/text-html.*
   :width: 398px
   :height: 52px

It features:

* Fully replaceable/customizable WYSIWYG editor.
* Text pre- and post-processing hooks.
* HTML sanitation/cleanup features.

The plugin is built on top of django-wysiwyg_, making it possible
to switch to any WYSIWYG editor of your choice.
The default editor is the YUI editor, because it works out of the box.
Other editors, like the CKEditor_, Redactor_ and TinyMCE_ are supported
with some additional configuration.
See the django-wysiwyg_ documentation for details.

.. important::

    There is no reason to feel constrained to a specific editor.
    Firstly, the editor can be configured by configuring django-wysiwyg_.
    Secondly, it's possible to create a different text plugin yourself,
    and let this plugin serve as canonical example.


Installation
------------

Install the dependencies via *pip*::

    pip install django-fluent-contents[text]

This installs the django-wysiwyg_ package.

Add the following settings to ``settings.py``:

.. code-block:: python

    INSTALLED_APPS += (
        'fluent_contents.plugins.text',
        'django_wysiwyg',
    )


Configuration
-------------

The following settings are available:

.. code-block:: python

    DJANGO_WYSIWYG_FLAVOR = "yui_advanced"

    FLUENT_TEXT_CLEAN_HTML = True
    FLUENT_TEXT_SANITIZE_HTML = True

    FLUENT_TEXT_PRE_PROCESSORS = ()
    FLUENT_TEXT_POST_PROCESSORS = ()


DJANGO_WYSIWYG_FLAVOR
~~~~~~~~~~~~~~~~~~~~~

The ``DJANGO_WYSIWYG_FLAVOR`` setting defines which WYSIWYG editor will be used.
As of django-wysiwyg_ 0.5.1, the following editors are available:

* **ckeditor** - The CKEditor_, formally known as FCKEditor.
* **redactor** - The Redactor_ editor (requires a license).
* **tinymce** - The TinyMCE_ editor, in simple mode.
* **tinymce_advanced** - The TinyMCE_ editor with many more toolbar buttons.
* **yui** - The YAHOO_ editor (the default)
* **yui_advanced** - The YAHOO_ editor with more toolbar buttons.

Additional editors can be easily added, as the setting refers to a set of templates names:

* django_wysiwyg/**flavor**/includes.html
* django_wysiwyg/**flavor**/editor_instance.html

For more information, see the documentation of django-wysiwyg_
about `extending django-wysiwyg <http://django-wysiwyg.readthedocs.org/en/latest/extending.html>`_.


FLUENT_TEXT_CLEAN_HTML
~~~~~~~~~~~~~~~~~~~~~~

If ``True``, the HTML tags will be rewritten to be well-formed.
This happens using either one of the following packages:

* html5lib_
* pytidylib_


FLUENT_TEXT_SANITIZE_HTML
~~~~~~~~~~~~~~~~~~~~~~~~~

if ``True``, unwanted HTML tags will be removed server side using html5lib_.


.. _FLUENT_TEXT_POST_FILTERS:
.. _FLUENT_TEXT_PRE_FILTERS:

FLUENT_TEXT_POST_FILTERS, FLUENT_TEXT_PRE_FILTERS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These settings allow text manipulation after saving.
Both settings accept a list of callable function names, which are called to update the text.

Examples:

.. code-block:: python

   FLUENT_TEXT_PRE_FILTERS = (
      'myapp.filters.cleanup_html',
      'myapp.filters.validate_html',
      'fluent_contents.plugins.text.filters.smartypants.smartypants_filter',
   )

   FLUENT_TEXT_POST_FILTERS = (
      'fluent_contents.plugins.text.filters.softhypen.softhypen_filter',
   )

The filter functions receive 2 parameters: the :class:`~fluent_contents.plugins.text.models.TextItem` model,
and the HTML text it can update. For example, see the smartypants filter:

.. code-block:: python

   from smartypants import smartypants

   def smartypants_filter(textitem, html):
      return smartypants(html)

The original :class:`~fluent_contents.plugins.text.models.TextItem` model is provided,
so the model fields such as ``textitem.language_code`` or ``textitem.placeholder`` or ``textitem.parent`` can
be read to have context.

The changes made by *pre*-filters are saved in the original text, and visible in the WYSIWYG editor after saving.
Thus, the pre-filter should be able to run multiple times over the same content.
Typical use cases of a pre-filter are:

* Validate HTML
* Sanitize HTML (e.g. using bleach_)
* Replace ``"``regular quotes``"`` with "smart quotes" (e.g. using smartypants_)

The *pre*-filters may also raise a :class:`~django.core.exceptions.ValidationError`,
as they are called during the form cleanup.

The changes made by *post*-filters are *not* stored in the original text, and won't be visible in the WYSIWYG editor.
This allows a free-form manipulation of the text, for example to:

* Add soft-hyphens in the code for better line breaking (e.g. using django-softhyphen_).
* Improve typography, such as avoiding text widows, highlighting ampersands, etc.. (using django-typogrify_).
* Highlight specific words.
* Reorganize citations for a scientific paper.
* Parse "short codes" - if you really must do so.
  *Please consider short codes a last resort.* It's recommended to create new plugins instead for complex integrations.


TinyMCE integration example
---------------------------

The WYSIWYG editor can be configured to allow end-users to make minimal styling choices.
The following configuration has proven to work nicely for most web sites,
save it as :file:`django_wysiwyg/tinymce_advanced/includes.html` in a Django template folder.
This code has the following features:

* django-filebrowser_ integration.
* Unnecessary styling is removed.
* Styling choices are limited to a single "format" box.
* It reads ``/static/frontend/css/tinymce.css``, allowing visual consistency between the editor and frontend web site.
* It defines ``body_class`` so any ``.text`` CSS selectors that style this plugin output work as expected.

.. code-block:: html+django

   {% extends "django_wysiwyg/tinymce/includes.html" %}

   <script>{# <- dummy element for editor formatting #}
   {% block django_wysiwyg_editor_config %}
       var django_wysiwyg_editor_config = {
           plugins: 'paste,autoresize,inlinepopups',
           strict_loading_mode: true,  // for pre 3.4 releases

           // Behavioral settings
           document_base_url: '/',
           relative_urls: false,
           custom_undo_redo_levels: 10,
           width: '610px',

           // Toolbars and layout
           theme: "advanced",
           theme_advanced_toolbar_location: 'top',
           theme_advanced_toolbar_align: 'left',
           theme_advanced_buttons1: 'styleselect,removeformat,cleanup,|,link,unlink,|,bullist,numlist,|,undo,redo,|,outdent,indent,|,sub,sup,|,image,charmap,anchor,hr,|,code',
           theme_advanced_buttons2: '',
           theme_advanced_buttons3: '',
           theme_advanced_blockformats: 'h3,h4,p',
           theme_advanced_resizing : true,

           // Integrate custom styling
           content_css: "{{ STATIC_URL }}frontend/css/tinymce.css",
           body_class: 'text',

           // Define user configurable styles
           style_formats: [
               {title: "Header 2", block: "h2"},
               {title: "Header 3", block: "h3"},
               {title: "Header 4", block: "h4"},
               {title: "Paragraph", block: "p"},
               {title: "Quote", block: "blockquote"},
               {title: "Bold", inline: "strong"},
               {title: "Emphasis", inline: "em"},
               {title: "Strikethrough", inline: "s"},
               {title: "Highlight word", inline: "span", classes: "highlight"},
               {title: "Small footnote", inline: "small"}
               //{title: "Code example", block: "pre"},
               //{title: "Code keyword", inline: "code"}
           ],

           // Define how TinyMCE formats things
           formats: {
             underline: {inline: 'u', exact: true}
             //strikethrough: {inline: 'del'},
           },
           //inline_styles: false,
           fix_list_elements: true,
           keep_styles: false,

           // Integrate filebrowser
           file_browser_callback: 'djangoFileBrowser'
       };

       function djangoFileBrowser(field_name, url, type, win) {
           var url = "{% url 'filebrowser:fb_browse' %}?pop=2&type=" + type;

           tinyMCE.activeEditor.windowManager.open(
           {
               'file': url,
               'width': 880,
               'height': 500,
               'resizable': "yes",
               'scrollbars': "yes",
               'inline': "no",
               'close_previous': "no"
           },
           {
               'window': win,
               'input': field_name,
               'editor_id': tinyMCE.selectedInstance.editorId
           });
           return false;
       }

   {% endblock %}
   </script>


.. _CKEditor: http://ckeditor.com/
.. _Redactor: http://redactorjs.com/
.. _TinyMCE: http://www.tinymce.com/
.. _YAHOO: http://developer.yahoo.com/yui/editor/
.. _bleach: https://github.com/mozilla/bleach
.. _django-ckeditor: https://github.com/shaunsephton/django-ckeditor
.. _django-filebrowser: https://github.com/smacker/django-filebrowser-no-grappelli
.. _django-softhyphen: https://github.com/datadesk/django-softhyphen/
.. _django-tinymce: https://github.com/aljosa/django-tinymce
.. _django-typogrify: https://github.com/chrisdrackett/django-typogrify
.. _django-wysiwyg: https://github.com/pydanny/django-wysiwyg
.. _html5lib: http://code.google.com/p/html5lib/
.. _pytidylib: http://countergram.com/open-source/pytidylib
.. _smartypants: https://pypi.python.org/pypi/smartypants/
