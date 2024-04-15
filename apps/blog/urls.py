from django.urls import path

from apps.blog.views import (
    ArticleListView,
    ArticleDetailView,
    ProjectListView,
    ProjectDetailView,
    TagListView,
    FAQListView,
    FAQDetailView,
    PrintCategoryListView,
    PrintCategoryDetailView
)

urlpatterns = [
    path('articles/', ArticleListView.as_view(), name='article_list'),
    path('articles/<int:pk>/', ArticleDetailView.as_view(), name='article_detail'),

    path('projects/', ProjectListView.as_view(), name='project_list'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='article_detail'),

    path('faq/', FAQListView.as_view(), name='faq-list'),
    path('faq/<int:faq_id>/', FAQDetailView.as_view(), name='faq-detail'),

    path('print-categories/', PrintCategoryListView.as_view(), name='faq-list'),
    path('print-categories/<int:category_id>/', PrintCategoryDetailView.as_view(), name='faq-detail'),

    path('tags/', TagListView.as_view(), name='tags')
]
