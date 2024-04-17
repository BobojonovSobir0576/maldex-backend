from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.banner.models import *
from apps.banner.api.serializers import (
    BannerListSerializer,
    BannerCarouselListSerializer
)

from utils.responses import (
    success_response,
)
from drf_yasg.utils import swagger_auto_schema


class BannerListView(APIView):
    permission_classes = [AllowAny]
    """ Banner Get View """

    @swagger_auto_schema(operation_description="Retrieve a list of banners",
                         tags=['Banners'],
                         responses={200: BannerListSerializer(many=True)})
    def get(self, request):
        queryset = Banner.objects.all().order_by('-created_at')
        serializer = BannerListSerializer(queryset, many=True, context={'request': request})
        return success_response(serializer.data)


class BannerCarouselListView(APIView):
    permission_classes = [AllowAny]
    """ Banner Carousel Get View """

    @swagger_auto_schema(operation_description="Retrieve a list of banner carousel",
                         tags=['Banner Carousel'],
                         responses={200: BannerListSerializer(many=True)})
    def get(self, request):
        queryset = BannerCarousel.objects.all().order_by('-created_at')
        serializer = BannerCarouselListSerializer(queryset, many=True, context={'request': request})
        return success_response(serializer.data)
