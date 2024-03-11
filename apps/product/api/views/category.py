from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.product.models import *
from apps.product.api.serializers import (
    CategoryListSerializers, ProductDetailSerializers, MainCategorySerializer
)
from utils.pagination import StandardResultsSetPagination
from utils.responses import (
    bad_request_response,
    success_response,
    success_created_response,
    success_deleted_response,
)
from utils.pagination import PaginationMethod
from utils.expected_fields import check_required_key
from drf_yasg.utils import swagger_auto_schema
from apps.product.utils import get_popular_categories


class CategoryListView(APIView):
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filter_fields = ["is_popular",]
    """ Category Get View """

    is_popular = openapi.Parameter('is_popular', openapi.IN_QUERY,
                                           description="Filter by Popular categories",
                                           type=openapi.TYPE_BOOLEAN)

    @swagger_auto_schema(operation_description="Retrieve a list of categories",
                         manual_parameters=[is_popular],
                         tags=['Categories'],
                         responses={200: CategoryListSerializers(many=True)})
    def get(self, request):
        queryset = ProductCategories.objects.all().order_by('-id').filter(parent__isnull=False)
        queryset = get_popular_categories(queryset, request)
        serializers = MainCategorySerializer(queryset, many=True,
                                              context={'request': request})
        return success_response(serializers.data)

    """ Category Post View """


    @swagger_auto_schema(request_body=CategoryListSerializers,
                         operation_description="Category create",
                         tags=['Categories'],
                         responses={201: CategoryListSerializers(many=False)})
    def post(self, request):
        valid_fields = {'name', 'icon'}
        unexpected_fields = check_required_key(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        serializers = CategoryListSerializers(data=request.data, context={'request': request})
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return success_created_response(serializers.data)
        return bad_request_response(serializers.errors)


class CategoryDetailView(APIView, PaginationMethod):
    pagination_class = StandardResultsSetPagination
    permission_classes = [AllowAny]
    """ Category Get View """
    @swagger_auto_schema(operation_description="Retrieve category or sub categories",
                         tags=['Categories'],
                         responses={200: CategoryListSerializers(many=True)})
    def get(self, request, pk):
        queryset = get_object_or_404(ProductCategories, pk=pk)
        serializers = MainCategorySerializer(queryset, context={'request': request, })
        return success_response(serializers.data)

    """ Category Put View """

    @swagger_auto_schema(request_body=CategoryListSerializers,
                         operation_description="Category update",
                         tags=['Categories'],
                         responses={200: CategoryListSerializers(many=False)})
    def put(self, request, pk):
        valid_fields = {'name', 'icon'}
        unexpected_fields = check_required_key(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        queryset = get_object_or_404(ProductCategories, pk=pk)
        serializers = CategoryListSerializers(instance=queryset, data=request.data,
                                              context={'request': request})
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return success_response(serializers.data)
        return bad_request_response(serializers.errors)

    """ Category Delete View """

    @swagger_auto_schema(operation_description="Delete a category",
                         tags=['Categories'],
                         responses={204: 'No content'})
    def delete(self, request, pk):
        queryset = get_object_or_404(ProductCategories, pk=pk)
        queryset.delete()
        return success_deleted_response("Successfully deleted")





