"""
The rendering support of the markup plugin.

This uses the backends from the actual text processing libraries.
"""
from django.core.exceptions import ImproperlyConfigured
from django.utils.safestring import mark_safe
from fluent_contents.plugins.markup import appsettings


def render_restructuredtext(text):
    from docutils.core import publish_parts
    parts = publish_parts(text, writer_name='html')
    # Want to return the html_body without the <div class="document" id="rst"> part
    return parts['body_pre_docinfo'] + parts['body'] + parts['footer']


def render_markdown(text):
    from markdown import markdown
    return markdown(text, ','.join(appsettings.FLUENT_MARKUP_MARKDOWN_EXTRAS))


def render_textile(text):
    from textile import textile
    return textile(text)

# Copy, and allow adding more options.
# Previously, this used django.contrib.markup.templatetags.markup,
# but since that's gone, the languages are defined here.
SUPPORTED_LANGUAGES = {
    'restructuredtext': render_restructuredtext,
    'markdown': render_markdown,
    'textile': render_textile
}

_languageNames = {
    'restructuredtext': 'reStructuredText',
    'markdown': 'Markdown',
    'textile': 'Textile',
}

if appsettings.FLUENT_MARKUP_USE_DJANGO_MARKUP:
    # With django-markup installed, it can be used instead of out default filters.
    # Since most django-markup filters are meant for simple text enhancements,
    # only use the filters which are really full text markup languages.
    # NOTE: the enhanced markdown above will also be replaced. Use the MARKUP_SETTINGS setting to configure django-markup instead.
    from django_markup.markup import formatter
    for filter_name, FilterClass in formatter.filter_list.items():
        real_filters = list(SUPPORTED_LANGUAGES.keys()) + ['creole']
        if filter_name in real_filters:
            _languageNames[filter_name] = FilterClass.title
            SUPPORTED_LANGUAGES[filter_name] = lambda text: mark_safe(formatter(text, filter_name))

# Format as choices
LANGUAGE_CHOICES = [(n, _languageNames.get(n, n.capitalize())) for n in list(SUPPORTED_LANGUAGES.keys())]
LANGUAGE_NAMES = dict(LANGUAGE_CHOICES)


def render_text(text, language=None):
    """
    Render the text, reuses the template filters provided by Django.
    """
    # Get the filter
    text_filter = SUPPORTED_LANGUAGES.get(language, None)
    if not text_filter:
        raise ImproperlyConfigured("markup filter does not exist: {0}. Valid options are: {1}".format(
            language, ', '.join(list(SUPPORTED_LANGUAGES.keys()))
        ))

    # Convert.
    return text_filter(text)
