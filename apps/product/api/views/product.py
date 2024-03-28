import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from drf_yasg import openapi
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.product.filters import ProductFilter
from apps.product.models import *
from apps.product.api.serializers import (
    ProductListSerializers, ProductDetailSerializers, ProductSerializer
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
from drf_yasg.utils import swagger_auto_schema


def get_subcategories(request, category_id):
    subcategories = list(ProductCategories.objects.filter(parent_id=category_id).values('id', 'name'))
    return JsonResponse(subcategories, safe=False)

def get_tertiary_categories(request, subcategory_id):
    tertiary_categories = list(ProductCategories.objects.filter(parent_id=subcategory_id).values('id', 'name'))
    return JsonResponse(tertiary_categories, safe=False)


class ProductsListView(APIView, PaginationMethod):
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    """ Products Get View """

    category = openapi.Parameter('category', openapi.IN_QUERY,
                                 description="Filter by category ID",
                                 type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID)

    @swagger_auto_schema(operation_description="Retrieve a list of products",
                         manual_parameters=[category],
                         tags=['Products'],
                         responses={200: ProductDetailSerializers(many=True)})
    def get(self, request):
        queryset = Products.objects.all()
        filterset = ProductFilter(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs
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


class ProductFileUploadView(APIView):
    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return JsonResponse({"error": "File is required."}, status=400)

        try:
            data = json.load(file)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON."}, status=400)

        # If the JSON is an array of objects, set many=True
        serializer = ProductSerializer(data=data, many=isinstance(data, list))
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, safe=False, status=201)
        else:
            return JsonResponse(serializer.errors, status=400)