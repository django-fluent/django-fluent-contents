from django.urls import path

from article.views import ArticleDetailView

urlpatterns = [
    path('<str:slug>/', ArticleDetailView.as_view(), name="article-details")
]
