from django.urls import path
from apps.banner.api.views import banner


urlpatterns = [
    path('', banner.BannerListView.as_view()),
    path('<uuid:pk>/', banner.BannerDetailView.as_view()),
    path('product/<uuid:pk>/', banner.BannerProductDetailView.as_view()),
    path('carousel/', banner.BannerCarouselListView.as_view()),
    path('carousel/<int:pk>/', banner.BannerCarouselDetailView.as_view()),
]
