from django.urls import path

from apps.blog.views import (
    ArticleListView,
    ArticleDetailView,
    ProjectListView,
    ProjectDetailView,
    FAQListView,
    FAQDetailView,
    PrintCategoryListView,
    PrintCategoryDetailView, get_article_tags, get_project_tags, LinkList, LinkDetail
)

urlpatterns = [
    # URLs for articles
    path('articles/', ArticleListView.as_view(), name='article_list'),  # List view for articles
    path('articles/tags/', get_article_tags, name='article_list'),  # List view for articles
    path('articles/<int:pk>/', ArticleDetailView.as_view(), name='article_detail'),  # Detail view

    # URLs for projects
    path('projects/', ProjectListView.as_view(), name='project_list'),  # List view for projects
    path('projects/tags/', get_project_tags, name='project_list'),  # List view for projects
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project_detail'),  # Detail view

    # URLs for FAQs
    path('faq/', FAQListView.as_view(), name='faq_list'),  # List view for FAQs
    path('faq/<int:faq_id>/', FAQDetailView.as_view(), name='faq_detail'),  # Detail view for a specific FAQ

    # URLs for print categories
    path('print-categories/', PrintCategoryListView.as_view(), name='print_category_list'),  # List view
    path('print-categories/<int:category_id>/', PrintCategoryDetailView.as_view(), name='print_category_detail'),

    # URLs for link tags
    path('link-tags/', LinkList.as_view(), name='links-list'),  # List view
    path('link-tags/<int:link_id>/', LinkDetail.as_view(), name='link-detail'),
]
