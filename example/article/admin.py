from article.models import Article, ArticleTextItem
from django.contrib import admin

from fluent_contents.admin import PlaceholderFieldAdmin


@admin.register(Article)
class ArticleAdmin(PlaceholderFieldAdmin):
    prepopulated_fields = {"slug": ("title",)}

    fieldsets = (
        (None, {"fields": ("title", "slug")}),
        ("Contents", {"fields": ("content",), "classes": ("plugin-holder",)}),
    )




# For debugging:

# class ArticleTextItemAdmin(admin.ModelAdmin):
#    list_display = ('text', 'parent')
#
# admin.site.register(ArticleTextItem, ArticleTextItemAdmin)
