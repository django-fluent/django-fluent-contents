"""
Using pygments to render the code.
"""
from pygments import highlight, styles
from pygments.lexers import get_all_lexers, get_lexer_by_name
from pygments.formatters.html import HtmlFormatter
from pygments.styles import get_all_styles
from django.utils.translation import ugettext as _
from fluent_contents.plugins.code import appsettings

STYLE_CHOICES = map(lambda x: (x,x), get_all_styles())
STYLE_CHOICES.sort(lambda x,y: cmp(x[1].lower(), y[1].lower()))

_languageChoices = map(lambda x: (x[1][0], x[0]), get_all_lexers())
_languageChoices.sort(lambda x,y: cmp(x[1].lower(), y[1].lower()))

LANGUAGE_CHOICES = tuple([t for t in _languageChoices if t[0] in appsettings.FLUENT_CODE_SHORTLIST])
if not appsettings.FLUENT_CODE_SHORTLIST_ONLY:
    LANGUAGE_CHOICES += (_('Combinations'), [t for t in _languageChoices if '+' in t[0]]),
    LANGUAGE_CHOICES += (_('Advanced'), [t for t in _languageChoices if '+' not in t[0] and t[0] not in appsettings.FLUENT_CODE_SHORTLIST]),


def render_code(instance, style_name='default'):
    # Some interesting options in the HtmlFormatter:
    # - nowrap       -> no wrap inside <pre>
    # - classprefix  -> prefix for the classnames
    # - noclasses    -> all inline styles.
    #
    # To get_style_defs(), you can pass a selector prefix.
    #
    style = styles.get_style_by_name(style_name)
    formatter = HtmlFormatter(linenos=instance.linenumbers, style=style, nowrap=True, classprefix='code%s-' % instance.pk)
    html = highlight(instance.code, get_lexer_by_name(instance.language), formatter)
    css = formatter.get_style_defs()

    # Included in a DIV, so the next item will be displayed below.
    return '<div class="code"><style type="text/css">' + css + '</style>\n<pre>' + html + '</pre></div>\n'

# TODO: Make code rendering more efficient, have one style definition in the head of the page!
