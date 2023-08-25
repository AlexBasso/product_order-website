from django.urls import path

from BlogApp.views import ArticleListView, ArticleDetailView, LatestArticlesFeed

app_name = 'blogapp'

urlpatterns = [
    path('articles/', ArticleListView.as_view(), name='articles'),
    path('articles/<int:pk>/', ArticleDetailView.as_view(), name='article'),
    path('articles/latest/feed/', LatestArticlesFeed(), name='articles-feed'),
    ]