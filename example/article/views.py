from django.views.generic.detail import DetailView

from article.models import Article


class ArticleDetailView(DetailView):
    model = Article
    template_name = "article/details.html"
