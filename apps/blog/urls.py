from django.urls import path

from apps.blog.views import (
    ArticleListView,
    ArticleDetailView,
    ProjectListView,
    ProjectDetailView,
    TagListView
)

urlpatterns = [
    path('articles/', ArticleListView.as_view(), name='article_list'),
    path('articles/<int:pk>/', ArticleDetailView.as_view(), name='article_detail'),

    path('projects/', ProjectListView.as_view(), name='project_list'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='article_detail'),

    path('tags/', TagListView.as_view(), name='tags')
]
