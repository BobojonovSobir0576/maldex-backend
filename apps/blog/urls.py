from django.urls import path

from apps.blog.views import ArticleListView, ArticleDetailView

urlpatterns = [
    path('articles/', ArticleListView.as_view(), name='article_list'),
    path('articles/<int:pk>/', ArticleDetailView.as_view(), name='article_detail'),
]
