from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.product.models import ProductCategories, ExternalCategory
from apps.product.api.serializers import (
    CategoryListSerializers, MainCategorySerializer, CategoryProductsSerializer, SubCategorySerializer,
    TertiaryCategorySerializer, CategoryAutoUploaderSerializer, ExternalCategoryListSerializer
)
from utils.pagination import StandardResultsSetPagination
from utils.responses import bad_request_response, success_response, success_created_response, success_deleted_response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.product.filters import ProductCategoryFilter


class CategoryListView(APIView):
    """
    API endpoint to list and create product categories.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Retrieve a list of categories",
        manual_parameters=[],
        tags=['Categories'],
        responses={200: CategoryListSerializers(many=True)}
    )
    def get(self, request):
        """
        Get all product categories.
        """
        queryset = ProductCategories.objects.all().prefetch_related('parent', 'children').filter(parent=None).order_by('order')
        filterset = ProductCategoryFilter(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs
        serializers = MainCategorySerializer(queryset, many=True, context={'request': request})
        return success_response(serializers.data)

    @swagger_auto_schema(
        request_body=MainCategorySerializer,
        operation_description="Create a new product category",
        tags=['Categories'],
        responses={201: MainCategorySerializer(many=False)}
    )
    def post(self, request):
        """
        Create a new product category.
        """
        serializers = MainCategorySerializer(data=request.data, context={'request': request})
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return success_created_response(serializers.data)
        return bad_request_response(serializers.errors)


class CategoryDetailView(APIView):
    """
    API endpoint to retrieve, update, and delete a specific product category.
    """
    pagination_class = StandardResultsSetPagination
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Retrieve a specific product category",
        tags=['Categories'],
        responses={200: CategoryListSerializers(many=True)}
    )
    def get(self, request, pk):
        """
        Retrieve a specific product category.
        """
        queryset = get_object_or_404(ProductCategories, pk=pk)
        serializers = MainCategorySerializer(queryset, context={'request': request})
        return success_response(serializers.data)

    @swagger_auto_schema(
        request_body=CategoryListSerializers,
        operation_description="Update a specific product category",
        tags=['Categories'],
        responses={200: CategoryListSerializers(many=False)}
    )
    def put(self, request, pk):
        """
        Update a specific product category.
        """
        queryset = get_object_or_404(ProductCategories, pk=pk)
        request.data._mutable = True
        request.data.pop('logo', None)
        request.data.pop('icon', None)
        request.data._mutable = False
        serializers = CategoryListSerializers(instance=queryset, data=request.data, context={
            'request': request,
            'logo': request.FILES.get('logo', None),
            'icon': request.FILES.get('icon', None)
        })
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return success_response(serializers.data)
        return bad_request_response(serializers.errors)

    @swagger_auto_schema(
        operation_description="Delete a specific product category",
        tags=['Categories'],
        responses={204: 'No content'}
    )
    def delete(self, request, pk):
        """
        Delete a specific product category.
        """
        queryset = get_object_or_404(ProductCategories, pk=pk)
        queryset.delete()
        return success_deleted_response("Successfully deleted")


class HomeCategoryView(APIView):
    """
    API endpoint to handle the home category.
    """
    pagination_class = StandardResultsSetPagination
    permission_classes = [AllowAny]

    @method_decorator(cache_page(600))
    @swagger_auto_schema(
        operation_description="Retrieve category or sub categories for home view",
        tags=['Categories'],
        responses={200: CategoryProductsSerializer}
    )
    def get(self, request):
        """
        Retrieve category or sub categories for home view.
        """
        category = ProductCategories.objects.filter(home=True).first()
        serializers = CategoryProductsSerializer(category, context={'request': request})
        return success_response(serializers.data)

    @swagger_auto_schema(
        operation_description="Create category or sub categories for home view",
        tags=['Categories'],
        responses={200: CategoryProductsSerializer}
    )
    def post(self, request):
        """
        Set a category as the home category.
        """
        category_id = request.data['id']
        category = get_object_or_404(ProductCategories, id=category_id)
        old_category = ProductCategories.objects.filter(home=True).first()
        old_category.home = False
        old_category.save()
        category.home = True
        category.save()

        serializers = CategoryProductsSerializer(category, context={'request': request})
        return success_response(serializers.data)


category_id_param = openapi.Parameter('category_id', openapi.IN_QUERY,
                                      description="Main Category ID",
                                      type=openapi.TYPE_STRING)
subcategory_id_param = openapi.Parameter('subcategory_id', openapi.IN_QUERY,
                                         description="Sub Category ID",
                                         type=openapi.TYPE_STRING)


@swagger_auto_schema(tags=['Categories'],
                     responses={200: SubCategorySerializer(many=True)},
                     operation_description='Get all sub categories',
                     method='GET')
@api_view(['GET'])
def get_maincategories(request):
    categories = list(ProductCategories.objects.filter(parent=None).values('id', 'name'))
    return success_response(categories)


@swagger_auto_schema(manual_parameters=[category_id_param], tags=['Categories'],
                     responses={200: SubCategorySerializer(many=True)},
                     operation_description='Get all sub categories',
                     method='GET')
@api_view(['GET'])
def get_subcategories(request, category_id):
    subcategories = list(ProductCategories.objects.filter(parent__id=category_id).values('id', 'name'))
    return success_response(subcategories)


@swagger_auto_schema(manual_parameters=[subcategory_id_param], tags=['Categories'],
                     responses={200: TertiaryCategorySerializer(many=True)},
                     operation_description='Get all tertiary categories',
                     method='GET')
@api_view(['GET'])
def get_tertiary_categories(request, subcategory_id):
    tertiary_categories = list(ProductCategories.objects.filter(parent_id=subcategory_id).values('id', 'name'))
    return success_response(tertiary_categories)


class ExternalCategoryList(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_description="Retrieve category or sub categories for home view",
        tags=['External Categories'],
        responses={200: CategoryProductsSerializer(many=True)}
    )

    def get(self, request):
        queryset = ExternalCategory.objects.all()
        serializer = ExternalCategoryListSerializer(queryset, many=True)
        return success_response(serializer.data)


class CategoryUploaderListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=CategoryAutoUploaderSerializer,
        operation_description="Upload new product category",
        tags=['Uploader Categories'],
        responses={201: CategoryAutoUploaderSerializer(many=False), 400: 'Bad request'}
    )
    def post(self, request):
        serializer = CategoryAutoUploaderSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            category = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
