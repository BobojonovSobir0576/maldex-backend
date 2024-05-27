from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.product.filters import ProductFilter
from apps.product.models import Products, ProductFilterModel, Colors
from apps.product.api.serializers import ProductDetailSerializers, \
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
    filter_id = openapi.Parameter('filter_id', openapi.IN_QUERY,
                                  description="Filter by Filter ID",
                                  type=openapi.FORMAT_UUID)
    search = openapi.Parameter('search', openapi.IN_QUERY,
                               description="Searching ...",
                               type=openapi.TYPE_STRING)
    material = openapi.Parameter('material', openapi.IN_QUERY,
                                 type=openapi.TYPE_STRING)
    brand = openapi.Parameter('brand', openapi.IN_QUERY,
                              type=openapi.TYPE_STRING)
    warehouse = openapi.Parameter('warehouse', openapi.IN_QUERY,
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
                         manual_parameters=[category_id, search, is_new, is_hit, is_popular,
                                            is_available, material, brand, warehouse],
                         tags=['Products'],
                         responses={200: ProductDetailSerializers(many=True)})
    def get(self, request):
        filter_id = request.query_params.get('filter_id')
        filter_model = ProductFilterModel.objects.filter(id=filter_id).first() if filter_id else None
        queryset = Products.objects.filter(
            filter_products__filter=filter_model) if filter_model else Products.objects.all()
        filterset = ProductFilter(request.query_params, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs
        queryset = queryset.order_by('-updated_at')
        serializers = super().page(queryset, ProductDetailSerializers, request)
        data = serializers.data
        # each sites product count
        data['sites_count'] = queryset.values('site').annotate(product_count=Count('id')).order_by('-product_count')
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


class BrandList(APIView):
    @swagger_auto_schema(
        tags=['Product'],
        responses={200: 'brand-list'}
    )
    def get(self, request):
        products = Products.objects.all()
        brands = products.values('brand').annotate(count=Count('brand')).order_by('-count')[:10]
        count = products.values('brand').distinct().count()
        return success_response({
            'count': count,
            'brands': brands,
        })


class MaterialList(APIView):
    @swagger_auto_schema(
        tags=['Product'],
        responses={200: 'brand-list'}
    )
    def get(self, request):
        products = Products.objects.all()
        materials = products.values('material').annotate(count=Count('material')).order_by('-count')[:10]
        count = products.values('material').distinct().count()
        return success_response({
            'count': count,
            'materials': materials,
        })


class ColorListView(APIView):
    @swagger_auto_schema(
        tags=['Product'],
        responses={200: 'colors-list'}
    )
    def get(self, request):
        colors = Colors.objects.annotate(products_count=Count('images__productID')).order_by('-products_count')[:10]
        return success_response({
            'colors': colors.values('name', 'products_count'),
        })
