from article.models import Article
from django.views.generic.detail import DetailView


class ArticleDetailView(DetailView):
    model = Article
    template_name = "article/details.html"
