from django.urls import path
from apps.banner.api.views import banner


urlpatterns = [
    path('', banner.BannerListView.as_view()),
    path('carousel/', banner.BannerCarouselListView.as_view())
]