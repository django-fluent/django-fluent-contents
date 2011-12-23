from django.contrib import admin
from article.models import Article, ArticleTextItem
from fluent_contents.admin import PlaceholderFieldAdmin


class ArticleAdmin(PlaceholderFieldAdmin):
    prepopulated_fields = {'slug': ('title',)}

    fieldsets = (
        (None, {
            'fields': ('title', 'slug'),
        }),
        ("Contents", {
            'fields': ('content',),
            'classes': ('plugin-holder',),
        })
    )

admin.site.register(Article, ArticleAdmin)



# For debugging:

#class ArticleTextItemAdmin(admin.ModelAdmin):
#    list_display = ('text', 'parent')
#
#admin.site.register(ArticleTextItem, ArticleTextItemAdmin)
