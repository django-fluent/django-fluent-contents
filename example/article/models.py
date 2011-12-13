from django.db import models
from content_placeholders.models.fields import PlaceholderField, PlaceholderRelation, ContentItemRelation
from content_placeholders.models import ContentItem


class Article(models.Model):
    title = models.CharField("Title", max_length=200)
    content = PlaceholderField("article_content", related_name='article_set_1')

    placeholder_set = PlaceholderRelation()
    contentitem_set = ContentItemRelation()

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    def __unicode__(self):
        return self.title


class ArticleTextItem(ContentItem):
    text = models.TextField("Text")

    class Meta:
        verbose_name = "Article text item"
        verbose_name_plural = "Article text items"

    def __unicode__(self):
        return self.text
