from django.contrib import admin
from article.models import Article, ArticleTextItem
from content_placeholders.admin import PlaceholderFieldAdmin


class ArticleAdmin(PlaceholderFieldAdmin):
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(Article, ArticleAdmin)



# For debugging:

class ArticleTextItemAdmin(admin.ModelAdmin):
    list_display = ('text', 'parent')

admin.site.register(ArticleTextItem, ArticleTextItemAdmin)
