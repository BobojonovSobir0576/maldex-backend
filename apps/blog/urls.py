from django.urls import path

from apps.blog.views import (
    ArticleListView,
    ArticleDetailView,
    ArticleTagListView,
    ProjectListView,
    ProjectDetailView,
    ProjectTagListView
)

urlpatterns = [
    path('articles/', ArticleListView.as_view(), name='article_list'),
    path('article-tags/', ArticleTagListView.as_view(), name='article_tag_list'),
    path('articles/<int:pk>/', ArticleDetailView.as_view(), name='article_detail'),

    path('projects/', ProjectListView.as_view(), name='project_list'),
    path('projects-tags/', ProjectTagListView.as_view(), name='article_tag_list'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='article_detail'),
]
