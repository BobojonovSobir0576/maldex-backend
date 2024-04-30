from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.product.models import ProductCategories
from apps.product.api.serializers import (
    CategoryListSerializers, MainCategorySerializer, CategoryProductsSerializer
)
from utils.pagination import StandardResultsSetPagination
from utils.responses import bad_request_response, success_response, success_created_response, success_deleted_response
from drf_yasg.utils import swagger_auto_schema
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
        queryset = ProductCategories.objects.all().prefetch_related('parent', 'children').filter(parent=None).order_by('-id', 'order')
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
        responses={200: CategoryProductsSerializer(many=True)}
    )
    def get(self, request):
        """
        Retrieve category or sub categories for home view.
        """
        category = ProductCategories.objects.filter(home=True).first()
        serializers = CategoryProductsSerializer(category, context={'request': request})
        return success_response(serializers.data)

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
