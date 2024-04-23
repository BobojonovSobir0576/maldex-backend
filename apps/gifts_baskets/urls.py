from django.urls import path
from apps.gifts_baskets.api.views import category
from apps.gifts_baskets.api.views import gift_basket
from apps.gifts_baskets.api.views import sets
from apps.gifts_baskets.api.views import admin_file


urlpatterns = [
    path('category/', category.GiftBasketCategoryListView.as_view()),
    path('category/<int:pk>/', category.GiftBasketCategoryDetailView.as_view()),

    path('', gift_basket.GiftBasketListView.as_view()),
    path('<int:pk>/', gift_basket.GiftBasketDetailView.as_view()),
    path('product/<int:pk>/', gift_basket.GiftsBasketProductDetailView.as_view()),
    path('image/<int:pk>/', gift_basket.GiftsBasketImageDetailSerializers.as_view()),

    path('set/catalogs/', sets.SetCategoryListView.as_view()),
    path('set/catalog/<int:pk>/', sets.SetCatalogDetailView.as_view()),

    path('set/product/<int:pk>/', sets.SetProductDetailView.as_view()),

    path('admin/files/', admin_file.AdminFilesListView.as_view()),
    path('admin/file/<int:pk>/', admin_file.AdminFilesDetailView.as_view()),

]
