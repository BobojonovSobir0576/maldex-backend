from django.urls import path
from apps.product.api.views import product, category
from apps.product.api.views import oasis_json
from apps.product.api.views.category import get_all_subcategories, CategoryMove
from apps.product.api.views.image import ProductImageView
from apps.product.api.views.product import SiteLogoView, get_counts, BrandList, MaterialList, ColorListView, PrintList
from apps.product.api.views.product_filter import FilterProductDetailView, FilterProductListView, \
    FilterProductsDetailView

urlpatterns = [
    # Product URLs
    path('', product.ProductsListView.as_view()),  # List view for all products
    path('sites-count/', product.SiteCountsView.as_view()),  # Endpoint to get site counts
    path('counts/', get_counts, name='products-counts'),  # Endpoint to get counts for product options
    path('<int:pk>/', product.ProductsDetailView.as_view()),  # Detail view for a specific product
    path('import/', oasis_json.ProductUploadView.as_view(), name='import_products'),  # Endpoint to import products
    path('categories/main_categories/', category.get_main_categories, name='main_categories'),
    path('categories/uploader/', category.CategoryUploaderListView.as_view()),
    path('external/categories/', category.ExternalCategoryList.as_view()),
    # Endpoint to get main categories
    path('categories/get_subcategories/<category_id>/', category.get_subcategories, name='get_subcategories'),
    # Endpoint to get subcategories of a main category
    path('categories/get_tertiary_categories/<subcategory_id>/', category.get_tertiary_categories,
         name='get_tertiary_categories'),  # Endpoint to get tertiary categories of a subcategory
    path('categories/subs/', get_all_subcategories, name='all_subcategories'),

    # Category URLs
    path('categories/', category.CategoryListView.as_view()),  # List view for all categories
    path('categories/move/', CategoryMove.as_view()),  # List view for all categories
    path('category/<int:pk>/', category.CategoryDetailView.as_view()),  # Detail view for a specific category
    path('category/<int:pk>/seen/', category.CategorySeenView.as_view()),  # Detail view for a specific category
    path('home-category/', category.HomeCategoryView.as_view()),  # View to get home category

    # Product Filters
    path('filters', FilterProductListView.as_view()),
    path('filters/<uuid:pk>', FilterProductDetailView.as_view()),
    path('filters/product/<uuid:pk>', FilterProductsDetailView.as_view()),
    # path('product/<uuid:pk>/', banner.BannerProductDetailView.as_view()),

    path('brands/', BrandList.as_view(), name='brand-list'),
    path('materials/', MaterialList.as_view(), name='material-list'),
    path('colors/', ColorListView.as_view(), name='color-list'),
    path('site-logos/', SiteLogoView.as_view(), name='site-logo-list'),
    path('prints/', PrintList.as_view(), name='site-logo-list'),

    # Image URLs
    path('image/<image_id>/', ProductImageView.as_view(), name='image'),  # Endpoint to get image by ID
    path('auto/uploader/', product.ProductAutoUploaderView.as_view()),
    path('auto/uploader/<int:pk>/', product.ProductAutoUploaderDetailView.as_view())
]
