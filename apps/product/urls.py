from django.urls import path
from apps.product.api.views import product, category
from apps.product.api.views import oasis_json
from apps.product.api.views.image import ProductImageView
from apps.product.api.views.product import get_counts

urlpatterns = [
    # Product URLs
    path('', product.ProductsListView.as_view()),  # List view for all products
    path('all/', product.AllProductsListView.as_view()),  # List view for all products
    path('counts/', get_counts, name='products-counts'),  # Endpoint to get counts for product options
    path('<int:pk>/', product.ProductsDetailView.as_view()),  # Detail view for a specific product
    path('import/', oasis_json.ProductUploadView.as_view(), name='import_products'),  # Endpoint to import products
    path('categories/main_categories/', category.get_maincategories, name='main_categories'),
    path('categories/uploader/', category.CategoryUploaderListView.as_view()),
    path('external/categories/', category.ExternalCategoryList.as_view()),
    # Endpoint to get main categories
    path('categories/get_subcategories/<category_id>/', category.get_subcategories, name='get_subcategories'),
    # Endpoint to get subcategories of a main category
    path('categories/get_tertiary_categories/<subcategory_id>/', category.get_tertiary_categories,
         name='get_tertiary_categories'),  # Endpoint to get tertiary categories of a subcategory

    # Category URLs
    path('categories/', category.CategoryListView.as_view()),  # List view for all categories
    path('category/<int:pk>/', category.CategoryDetailView.as_view()),  # Detail view for a specific category
    path('home-category/', category.HomeCategoryView.as_view()),  # View to get home category

    # Image URLs
    path('image/<image_id>/', ProductImageView.as_view(), name='image'),  # Endpoint to get image by ID
    path('auto/uploader/', product.ProductAutoUploaderView.as_view()),
    path('auto/uploader/<int:pk>/', product.ProductAutoUploaderDetailView.as_view())
]
