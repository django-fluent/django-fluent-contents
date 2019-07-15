import warnings

from .fluent_contents_tags import (
    PagePlaceholderNode,
    RenderPlaceholderNode,
    page_placeholder,
    register,
    render_placeholder,
)

warnings.warn(
    "fluent_contents.templatetags.placeholder_tags is deprecated; use fluent_contents_tags instead",
    DeprecationWarning,
)
