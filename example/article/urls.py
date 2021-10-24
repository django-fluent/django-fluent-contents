from article.views import ArticleDetailView
from django.urls import path

urlpatterns = [
    path("<str:slug>/", ArticleDetailView.as_view(), name="article-details"),
]
