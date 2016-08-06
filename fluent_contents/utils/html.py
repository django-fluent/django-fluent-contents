"""
Internal utilities to cleanup HTML 5 code.

These are used when FLUENT_TEXT_CLEANUP_HTML or FLUENT_TEXT_SANITIZE_HTML are enabled.

These are extracted from django-wysiwyg, so they can be used by default for all HTML fields.
It simplifies the dependencies a bit; html5lib can be directly mentioned as dependency.
"""
import warnings

from html5lib import treebuilders, treewalkers, HTMLParser
from html5lib.serializer import HTMLSerializer

try:
    from html5lib.sanitizer import HTMLSanitizer
except ImportError:
    HTMLSanitizer = None


def clean_html(input, sanitize=False):
    """
    Takes an HTML fragment and processes it using html5lib to ensure that the HTML is well-formed.

    :param sanitize: Remove unwanted HTML tags and attributes.

    >>> clean_html("<p>Foo<b>bar</b></p>")
    u'<p>Foo<b>bar</b></p>'
    >>> clean_html("<p>Foo<b>bar</b><i>Ooops!</p>")
    u'<p>Foo<b>bar</b><i>Ooops!</i></p>'
    >>> clean_html('<p>Foo<b>bar</b>& oops<a href="#foo&bar">This is a <>link</a></p>')
    u'<p>Foo<b>bar</b>&amp; oops<a href=#foo&amp;bar>This is a &lt;&gt;link</a></p>'
    """
    parser_kwargs = {}
    serializer_kwargs = {}
    if sanitize:
        if HTMLSanitizer is None:
            # new syntax as of 0.99999999/1.0b9 (Released on July 14, 2016)
            serializer_kwargs['sanitize'] = True
        else:
            parser_kwargs['tokenizer'] = HTMLSanitizer

    p = HTMLParser(tree=treebuilders.getTreeBuilder("dom"), **parser_kwargs)
    dom_tree = p.parseFragment(input)
    walker = treewalkers.getTreeWalker("dom")
    stream = walker(dom_tree)

    s = HTMLSerializer(omit_optional_tags=False, **serializer_kwargs)
    return "".join(s.serialize(stream))


def sanitize_html(input):
    """
    Removes any unwanted HTML tags and attributes, using html5lib.

    .. versionchanged:: 1.1.5

        Please use :func:`clean_html` instead with ``sanitize=True``.

    >>> sanitize_html("foobar<p>adf<i></p>abc</i>")
    u'foobar<p>adf<i></i></p><i>abc</i>'
    >>> sanitize_html('foobar<p style="color:red; remove:me; background-image: url(http://example.com/test.php?query_string=bad);">adf<script>alert("Uhoh!")</script><i></p>abc</i>')
    u'foobar<p style="color: red;">adf&lt;script&gt;alert("Uhoh!")&lt;/script&gt;<i></i></p><i>abc</i>'
    """
    warnings.warn("Please use clean_html(input, sanitize=True) instead", DeprecationWarning)
    return clean_html(input, sanitize=True)
