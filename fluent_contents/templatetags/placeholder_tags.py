import warnings
warnings.warn("fluent_contents.templatetags.placeholder_tags is deprecated; use fluent_contents_tags instead",
              DeprecationWarning)

from .fluent_contents_tags import (
    register,
    page_placeholder, PagePlaceholderNode,
    render_placeholder, RenderPlaceholderNode
)
