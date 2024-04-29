from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.banner.models import *
from apps.banner.api.serializers import (
    BannerListSerializer,
    BannerCarouselListSerializer, BannerProductListSerializer, BannerCarouselProductListSerializer
)

from utils.responses import (
    bad_request_response,
    success_response,
    success_created_response,
    success_deleted_response,
)
from utils.expected_fields import check_required_key
from drf_yasg.utils import swagger_auto_schema


class BannerListView(APIView):
    permission_classes = [AllowAny]
    """ Banner Get View """

    @method_decorator(cache_page(600))
    @swagger_auto_schema(operation_description="Retrieve a list of banners",
                         tags=['Banners'],
                         responses={200: BannerListSerializer(many=True)})
    def get(self, request):
        queryset = Banner.objects.all().order_by('-created_at')
        serializer = BannerListSerializer(queryset, many=True, context={'request': request})
        return success_response(serializer.data)

    @swagger_auto_schema(request_body=BannerListSerializer,
                         operation_description="Banner create",
                         tags=['Banners'],
                         responses={201: BannerListSerializer(many=False)})
    def post(self, request):
        valid_fields = {'name', 'product_data'}
        unexpected_fields = check_required_key(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        serializer = BannerListSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_created_response(serializer.data)
        return bad_request_response(serializer.errors)


class BannerDetailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(operation_description="Retrieve Banners",
                         tags=['Banners'],
                         responses={200: BannerListSerializer(many=True)})
    def get(self, request, pk):
        queryset = get_object_or_404(Banner, pk=pk)
        serializer = BannerListSerializer(queryset, context={'request': request, })
        return success_response(serializer.data)

    @swagger_auto_schema(request_body=BannerListSerializer,
                         operation_description="Banners update",
                         tags=['Banners'],
                         responses={200: BannerListSerializer(many=False)})
    def put(self, request, pk):
        valid_fields = {'name'}
        unexpected_fields = check_required_key(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        queryset = get_object_or_404(Banner, pk=pk)
        serializer = BannerListSerializer(instance=queryset, data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_response(serializer.data)
        return bad_request_response(serializer.errors)

    @swagger_auto_schema(operation_description="Delete a Banners",
                         tags=['Banners'],
                         responses={204: 'No content'})
    def delete(self, request, pk):
        queryset = get_object_or_404(Banner, pk=pk)
        queryset.delete()
        return success_deleted_response("Successfully deleted")


class BannerProductDetailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=BannerProductListSerializer,
                         operation_description="Banners product update",
                         tags=['Banner Product'],
                         responses={200: BannerProductListSerializer(many=False)})
    def put(self, request, pk):
        valid_fields = {'productID'}
        unexpected_fields = check_required_key(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        queryset = get_object_or_404(BannerProduct, pk=pk)
        serializer = BannerProductListSerializer(instance=queryset, data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_response(serializer.data)
        return bad_request_response(serializer.errors)

    @swagger_auto_schema(operation_description="Delete a Banners product",
                         tags=['Banner Product'],
                         responses={204: 'No content'})
    def delete(self, request, pk):
        queryset = get_object_or_404(BannerProduct, pk=pk)
        queryset.delete()
        return success_deleted_response("Successfully deleted")


class BannerCarouselListView(APIView):
    permission_classes = [AllowAny]
    """ Banner Carousel Get View """

    @method_decorator(cache_page(600))
    @swagger_auto_schema(operation_description="Retrieve a list of banner carousel",
                         tags=['Banner Carousel'],
                         responses={200: BannerCarouselListSerializer(many=True)})
    def get(self, request):
        queryset = BannerCarousel.objects.all().order_by('-created_at')
        serializer = BannerCarouselListSerializer(queryset, many=True, context={'request': request})
        return success_response(serializer.data)

    @swagger_auto_schema(request_body=BannerCarouselListSerializer,
                         operation_description="Banner create",
                         tags=['Banner Carousel'],
                         responses={201: BannerCarouselListSerializer(many=False)})
    def post(self, request):
        valid_fields = {'name', 'product_data'}
        unexpected_fields = check_required_key(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        serializer = BannerCarouselListSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_created_response(serializer.data)
        return bad_request_response(serializer.errors)


class BannerCarouselDetailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(operation_description="Retrieve Banners",
                         tags=['Banner Carousel'],
                         responses={200: BannerCarouselListSerializer(many=True)})
    def get(self, request, pk):
        queryset = get_object_or_404(BannerCarousel, pk=pk)
        serializer = BannerCarouselListSerializer(queryset, context={'request': request, })
        return success_response(serializer.data)

    @swagger_auto_schema(request_body=BannerCarouselListSerializer,
                         operation_description="Banners update",
                         tags=['Banner Carousel'],
                         responses={200: BannerCarouselListSerializer(many=False)})
    def put(self, request, pk):
        valid_fields = {'name'}
        unexpected_fields = check_required_key(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        queryset = get_object_or_404(BannerCarousel, pk=pk)
        serializer = BannerListSerializer(instance=queryset, data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_response(serializer.data)
        return bad_request_response(serializer.errors)

    @swagger_auto_schema(operation_description="Delete a Banners",
                         tags=['Banner Carousel'],
                         responses={204: 'No content'})
    def delete(self, request, pk):
        queryset = get_object_or_404(BannerCarousel, pk=pk)
        queryset.delete()
        return success_deleted_response("Successfully deleted")


class BannerCarouselProductDetailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=BannerCarouselProductListSerializer,
                         operation_description="Banners Carousel product update",
                         tags=['Banner Carousel Product'],
                         responses={200: BannerCarouselProductListSerializer(many=False)})
    def put(self, request, pk):
        valid_fields = {'productID'}
        unexpected_fields = check_required_key(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        queryset = get_object_or_404(BannerCarouselProduct, pk=pk)
        serializer = BannerCarouselProductListSerializer(instance=queryset, data=request.data,
                                                         context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_response(serializer.data)
        return bad_request_response(serializer.errors)

    @swagger_auto_schema(operation_description="Delete a Banners Carousel product",
                         tags=['Banner Carousel Product'],
                         responses={204: 'No content'})
    def delete(self, request, pk):
        queryset = get_object_or_404(BannerCarouselProduct, pk=pk)
        queryset.delete()
        return success_deleted_response("Successfully deleted")
