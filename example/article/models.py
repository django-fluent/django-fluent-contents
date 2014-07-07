from future.utils import python_2_unicode_compatible
from django.core.urlresolvers import reverse
from django.db import models
from fluent_contents.models.fields import PlaceholderField, PlaceholderRelation, ContentItemRelation
from fluent_contents.models import ContentItem


class Article(models.Model):
    title = models.CharField("Title", max_length=200)
    slug = models.SlugField("Slug", unique=True)
    content = PlaceholderField("article_content")

    placeholder_set = PlaceholderRelation()
    contentitem_set = ContentItemRelation()

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article-details', kwargs={'slug': self.slug})


@python_2_unicode_compatible
class ArticleTextItem(ContentItem):
    """
    This model can be placed on every placeholder field / page.
    """
    text = models.TextField("Text")

    class Meta:
        verbose_name = "Article text item"
        verbose_name_plural = "Article text items"

    def __str__(self):
        return self.text
