import warnings

from django.template import Library

from .fluent_contents_tags import (
    PagePlaceholderNode,
    RenderPlaceholderNode,
    page_placeholder as new_page_placeholder,
    render_placeholder as new_render_placeholder,
)


register = Library()


def warn():
    warnings.warn(
        "fluent_contents.templatetags.placeholder_tags is deprecated; use fluent_contents_tags instead",
        DeprecationWarning,
    )


@register.tag
def page_placeholder(parser, token):
    warn()
    return new_page_placeholder(parser, token)


@register.tag
def render_placeholder(parser, token):
    warn()
    return new_render_placeholder(parser, token)
