from django.urls import path
from apps.product.api.views import product, category
from apps.product.api.views import oasis_json
from apps.product.api.views.image import ProductImageView
from apps.product.api.views.product import get_counts

urlpatterns = [
    path('', product.ProductsListView.as_view()),
    path('all/', product.AllProductsListView.as_view()),
    path('option-counts/', get_counts, name='option-counts'),
    path('<int:pk>/', product.ProductsDetailView.as_view()),
    path('import/', oasis_json.ProductUploadView.as_view(), name='import_products'),
    path('categories/get_subcategories/<category_id>/', product.get_subcategories, name='get_subcategories'),
    path('categories/get_tertiary_categories/<subcategory_id>/', product.get_tertiary_categories,
         name='get_tertiary_categories'),

    path('categories/', category.CategoryListView.as_view()),
    path('category/<int:pk>/', category.CategoryDetailView.as_view()),
    path('home-category/', category.HomeCategoryView.as_view()),
    path('category/<int:pk>/change-order/', category.CategoryChangeOrderView.as_view()),

    path('image/<image_id>/', ProductImageView.as_view(), name='image'),
]
