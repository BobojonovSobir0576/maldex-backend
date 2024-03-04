from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.product.models import *
from apps.product.api.serializers import (
    ProductListSerializers, ProductDetailSerializers
)
from utils.responses import (
    bad_request_response,
    success_response,
    success_created_response,
    success_deleted_response,
)

from utils.expected_fields import check_required_key
from drf_yasg.utils import swagger_auto_schema
from utils.pagination import PaginationMethod, StandardResultsSetPagination


class ProductsListView(APIView, PaginationMethod):
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    """ Products Get View """

    @swagger_auto_schema(operation_description="Retrieve a list of products",
                         tags=['Products'],
                         responses={200: ProductDetailSerializers(many=True)})
    def get(self, request):
        queryset = Products.objects.all().order_by('-id')
        serializers = super().page(queryset, ProductDetailSerializers, request)
        return success_response(serializers.data)

    """ Products Post View """

    @swagger_auto_schema(request_body=ProductListSerializers,
                         operation_description="Products create",
                         tags=['Products'],
                         responses={201: ProductListSerializers(many=False)})
    def post(self, request):
        valid_fields = {'name', 'content', 'image', 'price', 'price_type', 'categoryId'}
        unexpected_fields = check_required_key(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        serializers = ProductListSerializers(data=request.data, context={'request': request})
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return success_created_response(serializers.data)
        return bad_request_response(serializers.errors)


class ProductsDetailView(APIView):
    permission_classes = [AllowAny]
    """ Products Get View """

    @swagger_auto_schema(operation_description="Retrieve a Products",
                         tags=['Products'],
                         responses={200: ProductDetailSerializers(many=True)})
    def get(self, request, pk):
        queryset = get_object_or_404(Products, pk=pk)
        serializers = ProductDetailSerializers(queryset, context={'request': request})
        return success_response(serializers.data)

    """ Products Put View """

    @swagger_auto_schema(request_body=ProductListSerializers,
                         operation_description="Products update",
                         tags=['Products'],
                         responses={200: ProductListSerializers(many=False)})
    def put(self, request, pk):
        valid_fields = {'name', 'content', 'image', 'price', 'price_type', 'categoryId'}
        unexpected_fields = check_required_key(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        queryset = get_object_or_404(Products, pk=pk)
        serializers = ProductListSerializers(instance=queryset, data=request.data,
                                              context={'request': request})
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return success_response(serializers.data)
        return bad_request_response(serializers.errors)

    """ Products Delete View """

    @swagger_auto_schema(operation_description="Delete a Products",
                         tags=['Products'],
                         responses={204: 'No content'})
    def delete(self, request, pk):
        queryset = get_object_or_404(Products, pk=pk)
        queryset.delete()
        return success_deleted_response("Successfully deleted")


