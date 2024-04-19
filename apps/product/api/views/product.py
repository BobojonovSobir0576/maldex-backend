from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from drf_yasg import openapi

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser

from apps.product.filters import ProductFilter
from apps.product.models import *
from apps.product.api.serializers import ProductDetailSerializers, SubCategorySerializer, \
    TertiaryCategorySerializer
from apps.product.proxy import TertiaryCategory, SubCategory
from utils.responses import (
    bad_request_response,
    success_response,
    success_deleted_response,
)

from utils.pagination import PaginationMethod, StandardResultsSetPagination
from drf_yasg.utils import swagger_auto_schema

category_id_param = openapi.Parameter('category_id', openapi.IN_QUERY,
                                      description="Main Category ID",
                                      type=openapi.TYPE_STRING)

subcategory_id_param = openapi.Parameter('subcategory_id', openapi.IN_QUERY,
                                         description="Sub Category ID",
                                         type=openapi.TYPE_STRING)


@swagger_auto_schema(manual_parameters=[category_id_param],
                     tags=['Categories'],
                     methods=['GET'],
                     responses={200: SubCategorySerializer(many=True)},
                     operation_description='Get all sub categories')
@api_view(['GET'])
def get_subcategories(request, category_id):
    subcategories = list(SubCategory.objects.filter(parent__id=category_id).values('id', 'name'))
    return JsonResponse(subcategories, safe=False)


@swagger_auto_schema(manual_parameters=[subcategory_id_param],
                     tags=['Categories'],
                     methods=['GET'],
                     responses={200: TertiaryCategorySerializer(many=True)},
                     operation_description='Get all tertiary categories')
@api_view(['GET'])
def get_tertiary_categories(request, subcategory_id):
    tertiary_categories = list(TertiaryCategory.objects.filter(parent_id=subcategory_id).values('id', 'name'))
    return JsonResponse(tertiary_categories, safe=False)


class ProductsListView(APIView, PaginationMethod):
    permission_classes = [AllowAny]
    parser_class = (FileUploadParser, MultiPartParser, FormParser)
    serializer_class = ProductDetailSerializers
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

    @swagger_auto_schema(request_body=ProductDetailSerializers,
                         operation_description="Products create",
                         tags=['Products'],
                         responses={201: ProductDetailSerializers(many=False)})
    def post(self, request):
        # valid_fields = {'name', 'content', 'image', 'price', 'price_type', 'categoryId'}
        # unexpected_fields = check_required_key(request, valid_fields)
        # if unexpected_fields:
        #     return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        product_serializer = ProductDetailSerializers(data=request.data, context={'request': request})
        if product_serializer.is_valid(raise_exception=True):
            product_serializer.save()
            return Response(product_serializer.data, status=status.HTTP_201_CREATED)
        return Response(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductsDetailView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ProductDetailSerializers

    """ Products Get View """

    @swagger_auto_schema(operation_description="Retrieve a Products",
                         tags=['Products'],
                         responses={200: ProductDetailSerializers(many=False)})
    def get(self, request, pk):
        queryset = get_object_or_404(Products, pk=pk)
        serializers = ProductDetailSerializers(instance=queryset, context={'request': request}, many=False)
        return success_response(serializers.data)

    """ Products Put View """

    @swagger_auto_schema(request_body=ProductDetailSerializers,
                         operation_description="Products update",
                         tags=['Products'],
                         responses={200: ProductDetailSerializers(many=False)})
    def put(self, request, pk):
        product_instance = get_object_or_404(Products, pk=pk)
        print(request.data)
        serializer = ProductDetailSerializers(instance=product_instance, data=request.data,
                                              context={'request': request})
        request.data._mutable = True
        category_id = request.data.get('categoryId', 'null')
        if category_id == 'null':
            request.data.pop('categoryId')
        request.data._mutable = False

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_response(serializer.data)

        return bad_request_response(serializer.errors)

    """ Products Delete View """

    @swagger_auto_schema(operation_description="Delete a Products",
                         tags=['Products'],
                         responses={204: 'No content'})
    def delete(self, request, pk):
        queryset = get_object_or_404(Products, pk=pk)
        queryset.delete()
        return success_deleted_response("Successfully deleted")
