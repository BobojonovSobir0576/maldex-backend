from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.product.filters import ProductFilter
from apps.product.models import Products
from apps.product.api.serializers import ProductDetailSerializers, ProductListSerializers, \
    ProductAutoUploaderSerializer, ProductAutoUploaderDetailSerializer
from utils.responses import bad_request_response, success_response, success_deleted_response, success_created_response
from utils.pagination import PaginationMethod, StandardResultsSetPagination



@swagger_auto_schema(tags=['Products'],
                     operation_description='Get the number of NEW, HIT, POPULAR products',
                     method='GET')
@api_view(['GET'])
def get_counts(request):
    new_product_count = Products.objects.filter(is_new=True).count()
    hit_product_count = Products.objects.filter(is_hit=True).count()
    popular_product_count = Products.objects.filter(is_popular=True).count()
    return success_response({
        'new': new_product_count,
        'hit': hit_product_count,
        'popular': popular_product_count
    })


class ProductsListView(APIView, PaginationMethod):
    permission_classes = [AllowAny]
    parser_class = (FileUploadParser, MultiPartParser, FormParser)
    serializer_class = ProductDetailSerializers
    pagination_class = StandardResultsSetPagination

    category_id = openapi.Parameter('category_id', openapi.IN_QUERY,
                                    description="Filter by category ID",
                                    type=openapi.TYPE_STRING)
    search = openapi.Parameter('search', openapi.IN_QUERY,
                               description="Searching ...",
                               type=openapi.TYPE_STRING)
    is_new = openapi.Parameter('is_new', openapi.IN_QUERY,
                               description="NEW products",
                               type=openapi.TYPE_BOOLEAN)
    is_hit = openapi.Parameter('is_hit', openapi.IN_QUERY,
                               description="HIT products",
                               type=openapi.TYPE_BOOLEAN)
    is_popular = openapi.Parameter('is_popular', openapi.IN_QUERY,
                                   description="POPULAR products",
                                   type=openapi.TYPE_BOOLEAN)
    is_available = openapi.Parameter('is_available', openapi.IN_QUERY,
                                     description="AVAILABLE products",
                                     type=openapi.TYPE_BOOLEAN)

    @swagger_auto_schema(operation_description="Retrieve a list of products",
                         manual_parameters=[category_id, search, is_new, is_hit, is_popular, is_available],
                         tags=['Products'],
                         responses={200: ProductDetailSerializers(many=True)})
    def get(self, request):
        queryset = Products.objects.all()
        filterset = ProductFilter(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs
        serializers = super().page(queryset, ProductDetailSerializers, request)
        return success_response(serializers.data)

    @swagger_auto_schema(request_body=ProductDetailSerializers,
                         operation_description="Products create",
                         tags=['Products'],
                         responses={201: ProductDetailSerializers(many=False)})
    def post(self, request):
        product_serializer = ProductDetailSerializers(data=request.data, context={'request': request})
        if product_serializer.is_valid(raise_exception=True):
            product_serializer.save()
            return success_created_response(product_serializer.data)
        return bad_request_response(product_serializer.errors)


class AllProductsListView(APIView):
    permission_classes = [AllowAny]
    parser_class = (FileUploadParser, MultiPartParser, FormParser)
    serializer_class = ProductDetailSerializers
    pagination_class = StandardResultsSetPagination

    category_id = openapi.Parameter('category_id', openapi.IN_QUERY,
                                    description="Filter by category ID",
                                    type=openapi.TYPE_STRING)
    search = openapi.Parameter('search', openapi.IN_QUERY,
                               description="Searching ...",
                               type=openapi.TYPE_STRING)
    is_new = openapi.Parameter('is_new', openapi.IN_QUERY,
                               description="NEW products",
                               type=openapi.TYPE_BOOLEAN)
    is_hit = openapi.Parameter('is_hit', openapi.IN_QUERY,
                               description="HIT products",
                               type=openapi.TYPE_BOOLEAN)
    is_popular = openapi.Parameter('is_popular', openapi.IN_QUERY,
                                   description="POPULAR products",
                                   type=openapi.TYPE_BOOLEAN)
    is_available = openapi.Parameter('is_available', openapi.IN_QUERY,
                                     description="AVAILABLE products",
                                     type=openapi.TYPE_BOOLEAN)

    @swagger_auto_schema(operation_description="Retrieve a list of products",
                         manual_parameters=[category_id, search, is_new, is_hit, is_popular, is_available],
                         tags=['Products'],
                         responses={200: ProductListSerializers(many=True)})
    def get(self, request):
        queryset = Products.objects.all().order_by('-id')
        filterset = ProductFilter(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs
        serializers = ProductListSerializers(queryset[:200], many=True, context={'request': request})
        return success_response(serializers.data)


class ProductsDetailView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ProductDetailSerializers

    @swagger_auto_schema(operation_description="Retrieve a Products",
                         tags=['Products'],
                         responses={200: ProductDetailSerializers(many=False)})
    def get(self, request, pk):
        queryset = get_object_or_404(Products, pk=pk)
        serializers = ProductDetailSerializers(instance=queryset, context={'request': request}, many=False)
        return success_response(serializers.data)

    @swagger_auto_schema(request_body=ProductDetailSerializers,
                         operation_description="Products update",
                         tags=['Products'],
                         responses={200: ProductDetailSerializers(many=False)})
    def put(self, request, pk):
        product_instance = get_object_or_404(Products, pk=pk)
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

    @swagger_auto_schema(operation_description="Delete a Products",
                         tags=['Products'],
                         responses={204: 'No content'})
    def delete(self, request, pk):
        queryset = get_object_or_404(Products, pk=pk)
        queryset.delete()
        return success_deleted_response("Successfully deleted")


class ProductAutoUploaderView(APIView):

    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=ProductAutoUploaderSerializer,
                         operation_description="Products Auto Uploader",
                         tags=['Products Auto Uploader'],
                         responses={201: ProductAutoUploaderSerializer(many=False)})
    def post(self, request):
        # print(request.data)
        product_serializer = ProductAutoUploaderSerializer(data=request.data, context={'request': request})
        if product_serializer.is_valid(raise_exception=True):
            product_serializer.save()
            return success_created_response(product_serializer.data)
        return bad_request_response(product_serializer.errors)


class ProductAutoUploaderDetailView(APIView):
    @swagger_auto_schema(request_body=ProductAutoUploaderDetailSerializer,
                         operation_description="Products auto uploader update",
                         tags=['Products Auto Uploader'],
                         responses={200: ProductAutoUploaderDetailSerializer(many=False)})
    def put(self, request, pk):
        product_instance = get_object_or_404(Products, pk=pk)
        serializer = ProductAutoUploaderDetailSerializer(instance=product_instance, data=request.data,
                                              context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_response(serializer.data)
        return bad_request_response(serializer.errors)
