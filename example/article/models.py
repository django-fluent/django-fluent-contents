from __future__ import unicode_literals
from django.db import models
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from fluent_contents.models.fields import PlaceholderField, PlaceholderRelation, ContentItemRelation
from fluent_contents.models import ContentItem, ContentItemManager


@python_2_unicode_compatible
class Article(models.Model):
    title = models.CharField("Title", max_length=200)
    slug = models.SlugField("Slug", unique=True)
    content = PlaceholderField("article_content")

    placeholder_set = PlaceholderRelation()
    contentitem_set = ContentItemRelation()

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article-details', kwargs={'slug': self.slug})


@python_2_unicode_compatible
class ArticleTextItem(ContentItem):
    """
    This model can be placed on every placeholder field / page.
    """
    text = models.TextField("Text")

    objects = ContentItemManager()  # Avoid Django 1.10 migrations

    class Meta:
        verbose_name = "Article text item"
        verbose_name_plural = "Article text items"

    def __str__(self):
        return self.text
