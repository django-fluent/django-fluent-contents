from django.contrib import admin
from article.models import Article, ArticleTextItem
from content_placeholders.admin import PlaceholderFieldAdmin, PlaceholderInline, get_content_item_inlines


class ArticleAdmin(PlaceholderFieldAdmin):
    inlines = [PlaceholderInline] + get_content_item_inlines()


admin.site.register(Article, ArticleAdmin)
admin.site.register(ArticleTextItem)
