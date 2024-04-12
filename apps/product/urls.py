from django.urls import path
from apps.product.api.views import product, category
from apps.product.api.views import oasis_json

urlpatterns = [
    path('', product.ProductsListView.as_view()),
    path('<int:pk>/', product.ProductsDetailView.as_view()),
    path('import/', oasis_json.ProductUploadView.as_view(), name='import_products'),
    path('categories/get_subcategories/<category_id>/', product.get_subcategories, name='get_subcategories'),
    path('categories/get_tertiary_categories/<uuid:subcategory_id>/', product.get_tertiary_categories,
         name='get_tertiary_categories'),

    path('categories/', category.CategoryListView.as_view()),
    path('category/<int:pk>/', category.CategoryDetailView.as_view()),
    path('category/<int:pk>/change-order/', category.CategoryChangeOrderView.as_view()),
]
