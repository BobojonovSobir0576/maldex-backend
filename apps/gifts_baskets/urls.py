from django.urls import path
from apps.gifts_baskets.api.views import category
from apps.gifts_baskets.api.views import gift_basket
from apps.gifts_baskets.api.views import sets


urlpatterns = [
    path('category/', category.GiftBasketCategoryListView.as_view()),
    path('category/<int:pk>/', category.GiftBasketCategoryDetailView.as_view()),

    path('', gift_basket.GiftBasketListView.as_view()),
    path('<int:pk>/', gift_basket.GiftBasketDetailView.as_view()),
    path('product/<int:pk>/', gift_basket.GiftsBasketProductDetailView.as_view()),
    path('image/<int:pk>/', gift_basket.GiftsBasketImageDetailSerializers.as_view()),

    path('set/catalogs/', sets.SetCategoryListView.as_view()),
    path('set/catalog/<int:id>/', sets.SetCatalogDetailView.as_view()),

    path('set/product/<int:id>/', sets.SetProductDetailView.as_view()),
]