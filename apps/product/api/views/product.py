from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.product.filters import ProductFilter
from apps.product.models import *
from apps.product.api.serializers import ProductListSerializers, ProductDetailSerializers
from utils.responses import (
    bad_request_response,
    success_response,
    success_created_response,
    success_deleted_response,
)

from utils.expected_fields import check_required_key
from utils.pagination import PaginationMethod, StandardResultsSetPagination
from drf_yasg.utils import swagger_auto_schema


def get_subcategories(request, category_id):
    subcategories = list(ProductCategories.objects.filter(parent__id=category_id).values('id', 'name'))
    return JsonResponse(subcategories, safe=False)


def get_tertiary_categories(request, subcategory_id):
    tertiary_categories = list(ProductCategories.objects.filter(parent_id=subcategory_id).values('id', 'name'))
    return JsonResponse(tertiary_categories, safe=False)


class ProductsListView(APIView, PaginationMethod):
    permission_classes = [AllowAny]
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

    @swagger_auto_schema(request_body=ProductListSerializers,
                         operation_description="Products create",
                         tags=['Products'],
                         responses={201: ProductListSerializers(many=False)})
    def post(self, request):
        # valid_fields = {'name', 'content', 'image', 'price', 'price_type', 'categoryId'}
        # unexpected_fields = check_required_key(request, valid_fields)
        # if unexpected_fields:
        #     return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        serializers = ProductListSerializers(data=request.data, context={'request': request})
        if serializers.is_valid(raise_exception=True):
            serializers.save()

            product = Products.objects.get(id=request.data['id'])
            images = request.data.pop('images')
            serializers.data['image_set'] = []
            for image in images:
                img = image['image']
                color = image['color']
                color_model = Colors.objects.filter(name=color).first()
                if not color_model:
                    color_model = Colors.objects.create(name=color)
                image_model = ProductImage.objects.create(product=product, image=img, color=color_model)
                serializers.data['image_set'].append(image_model)

            return success_created_response(serializers.data)
        return bad_request_response(serializers.errors)


class ProductsDetailView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ProductDetailSerializers
    """ Products Get View """

    @swagger_auto_schema(operation_description="Retrieve a Products",
                         tags=['Products'],
                         responses={200: ProductDetailSerializers(many=True)})
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
        # valid_fields = {'name', 'content', 'image', 'price', 'price_type', 'categoryId'}
        # unexpected_fields = check_required_key(request, valid_fields)
        # if unexpected_fields:
        #     return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        queryset = get_object_or_404(Products, pk=pk)
        serializers = ProductDetailSerializers(instance=queryset, data=request.data,
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
