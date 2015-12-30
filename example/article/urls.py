from django.conf.urls import url
from article.views import ArticleDetailView

urlpatterns = [
    url(r'^(?P<slug>[^/]+)/$', ArticleDetailView.as_view(), name='article-details'),
]
