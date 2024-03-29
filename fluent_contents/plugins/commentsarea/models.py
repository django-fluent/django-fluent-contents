from django.db import models
from django.db.models import signals
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from fluent_utils.softdeps.comments import get_model as get_comment_model
from fluent_utils.softdeps.comments import signals as comments_signals

from fluent_contents.models import ContentItem, ContentItemManager

CommentModel = get_comment_model()


class CommentsAreaItem(ContentItem):
    allow_new = models.BooleanField(_("Allow posting new comments"), default=True)

    objects = ContentItemManager()  # Avoid Django 1.10 migrations

    class Meta:
        verbose_name = _("Comments area")
        verbose_name_plural = _("Comments areas")

    def __str__(self):
        return ""


def clear_commentarea_cache(comment):
    """
    Clean the plugin output cache of a rendered plugin.
    """
    parent = comment.content_object
    for instance in CommentsAreaItem.objects.parent(parent):
        instance.clear_cache()


# Allow admin changes to invalidate the cache.
@receiver(signals.post_save, sender=CommentModel)
@receiver(signals.post_delete, sender=CommentModel)
def _on_comment_changed(instance, **kwargs):
    clear_commentarea_cache(instance)


# Allow frontend actions to invalidate the cache.
@receiver(comments_signals.comment_was_posted)
@receiver(comments_signals.comment_was_flagged)
def _on_comment_posted(comment, **kwargs):
    clear_commentarea_cache(comment)
