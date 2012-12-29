"""
A proxy to automatically switch to the ``threadedcomments`` template tags if they are available.
"""
from django.contrib.comments.templatetags import comments
from django import template
from django.template.loader import render_to_string
from fluent_contents.plugins.commentsarea import appsettings

register = template.Library()


class RenderCommentsTreeNode(comments.CommentListNode):
    """
    A custom node to render the comments tree, for django-threadedcomments.
    """
    template_name = "list.html"

    @classmethod
    def handle_token(cls, parser, token):
        tokens = token.contents.split()
        if tokens[1] != 'for':
            raise template.TemplateSyntaxError("Second argument in %r tag must be 'for'" % tokens[0])

        # {% render_comment_list for obj %}
        if len(tokens) == 3:
            return cls(object_expr=parser.compile_filter(tokens[2]))
        else:
            raise template.TemplateSyntaxError("%r tag requires 2 arguments" % tokens[0])

    def render(self, context):
        ctype, object_pk = self.get_target_ctype_pk(context)
        if object_pk:
            template_search_list = [
                "comments/%s/%s/%s" % (ctype.app_label, ctype.model, self.template_name),
                "comments/%s/%s" % (ctype.app_label, self.template_name),
                "comments/%s" % self.template_name
            ]
            qs = self.get_query_set(context)
            context.push()
            liststr = render_to_string(template_search_list, {
                "comment_list" : self.get_context_value_from_queryset(context, qs)
            }, context)
            context.pop()
            return liststr
        else:
            return ''


if appsettings.FLUENT_COMMENTSAREA_THREADEDCOMMENTS:
    # Support threadedcomments
    from threadedcomments.templatetags import threadedcomments_tags  # If this import fails, the module version is too old.
    register.filters.update(threadedcomments_tags.register.filters)
    register.tags.update(threadedcomments_tags.register.tags)

    # https://github.com/HonzaKral/django-threadedcomments still doesn't have a 'render_comment_list' tag,
    # the pull request at https://github.com/HonzaKral/django-threadedcomments/pull/39 adds this.
    if 'render_comment_list' not in register.tags:
        # Add missing render_comment_list tag.
        @register.tag
        def render_comment_list(parser, token):
            return RenderCommentsTreeNode.handle_token(parser, token)

else:
    # Standard comments
    register.filters.update(comments.register.filters)
    register.tags.update(comments.register.tags)
