from django.contrib import comments
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models import signals
from django.contrib.comments import signals as comments_signals
from fluent_contents.models import ContentItem


class CommentsAreaItem(ContentItem):
    allow_new = models.BooleanField(_("Allow posting new comments"), default=True)

    class Meta:
        verbose_name = _('Comments area')
        verbose_name_plural = _('Comments areas')

    def __unicode__(self):
        return u''


def clear_commentarea_cache(comment):
    """
    Clean the plugin output cache of a rendered plugin.
    """
    parent = comment.content_object
    for instance in CommentsAreaItem.objects.parent(parent):
        instance.clear_cache()


# Allow admin changes to invalidate the cache.
def _on_comment_changed(instance, **kwargs):
    clear_commentarea_cache(instance)

CommentModel = comments.get_model()
signals.post_save.connect(_on_comment_changed, sender=CommentModel)
signals.post_delete.connect(_on_comment_changed, sender=CommentModel)


# Allow frontend actions to invalidate the cache.
def _on_comment_posted(comment, **kwargs):
    clear_commentarea_cache(comment)

comments_signals.comment_was_posted.connect(_on_comment_posted)
comments_signals.comment_was_flagged.connect(_on_comment_posted)
