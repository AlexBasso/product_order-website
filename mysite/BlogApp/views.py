from django.contrib.syndication.views import Feed
from django.views.generic import ListView, DetailView
from django.urls import reverse, reverse_lazy

from BlogApp.models import Article


class ArticleListView(ListView):
    # queryset = Article.objects.defer('content').select_related('author').prefetch_related('category', 'tags').all()
    queryset = (
        Article.objects
        .filter(pub_date__isnull=False)
        .order_by("-pub_date")
    )
    template_name = 'BlogApp/articles-list.html'
    context_object_name = "articles"


class ArticleDetailView(DetailView):
    model = Article


class LatestArticlesFeed(Feed):
    title = "Blog articles (latest)"
    description = "Update on changes and additions blog articles"
    link = reverse_lazy("blogapp:articles")

    def items(self):
        return (
            Article.objects
            .filter(pub_date__isnull=False)
            .order_by("-pub_date")[:5]
        )

    def item_title(self, item: Article):
        return item.title

    def item_description(self, item: Article):
        return item.content[:300]

    # changed location to models.py
    # def item_link(self, item: Article):
    #     return reverse("blogapp:article", kwargs={"pk": item.pk})
