from django.conf.urls.defaults import *
from article.views import ArticleDetailView

urlpatterns = patterns('',
    url(r'^(?P<slug>[^/]+)/$', ArticleDetailView.as_view(), name='article-details'),
)
