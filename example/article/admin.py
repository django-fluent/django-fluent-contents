from django.contrib import admin
from article.models import Article, ArticleTextItem
from content_placeholders.admin import PlaceholderFieldAdmin


class ArticleAdmin(PlaceholderFieldAdmin):
    pass


admin.site.register(Article, ArticleAdmin)
admin.site.register(ArticleTextItem)
