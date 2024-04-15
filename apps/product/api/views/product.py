from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from drf_yasg import openapi

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser

from apps.product.filters import ProductFilter
from apps.product.models import *
from apps.product.api.serializers import ProductImageSerializer, ProductDetailSerializers
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
            product_instance = product_serializer.save()           
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
        serializer = ProductDetailSerializers(instance=product_instance, data=request.data, context={'request': request})

        if serializer.is_valid(raise_exception=True):
            # Update product fields
            serializer.save()

            # Handle adding or changing images
            images_data = request.data.get('images', [])
            for image_data in images_data:
                # Assuming image_data contains image information along with color
                color_name = image_data.get('color')
                color_instance, _ = Colors.objects.get_or_create(name=color_name)
                ProductImage.objects.update_or_create(
                    productID=product_instance,
                    colorID=color_instance,
                    defaults={
                        'image': image_data.get('image'),  # Assuming 'image' field represents the image URL
                        # Add other fields as needed
                    }
                )

            # Handle deleting images
            deleted_image_ids = request.data.get('deleted_image_ids', [])
            if deleted_image_ids:
                ProductImage.objects.filter(productID=product_instance, id__in=deleted_image_ids).delete()

            # Return updated product data
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
