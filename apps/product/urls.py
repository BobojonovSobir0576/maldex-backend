from django.urls import path
from apps.product.api.views import product, category

urlpatterns = [
    path('', product.ProductsListView.as_view()),
    path('<int:pk>/', product.ProductsDetailView.as_view()),

    path('categories/', category.CategoryListView.as_view()),
    path('category/<int:pk>/', category.CategoryDetailView.as_view())
]