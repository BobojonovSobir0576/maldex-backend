from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.product.api.serializers import FilterProductSerializer, ProductFilterProductSerializer
from apps.product.models import ProductFilterProducts, ProductFilterModel
from utils.expected_fields import check_required_key
from utils.responses import success_response, success_created_response, bad_request_response, success_deleted_response


class FilterProductListView(APIView):
    permission_classes = [AllowAny]
    """ Banner Get View """

    @swagger_auto_schema(operation_description="Retrieve a list of banners",
                         tags=['Filter Product'],
                         responses={200: FilterProductSerializer(many=True)})
    def get(self, request):
        queryset = ProductFilterModel.objects.all().order_by('-created_at')
        serializer = FilterProductSerializer(queryset, many=True, context={'request': request})
        return success_response(serializer.data)

    @swagger_auto_schema(request_body=FilterProductSerializer,
                         operation_description="Banner create",
                         tags=['Filter Product'],
                         responses={201: FilterProductSerializer(many=False)})
    def post(self, request):
        valid_fields = {'title', 'product_data'}
        unexpected_fields = check_required_key(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        serializer = FilterProductSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_created_response(serializer.data)
        return bad_request_response(serializer.errors)


class FilterProductDetailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(operation_description="Retrieve Banners",
                         tags=['Filter Product'],
                         responses={200: FilterProductSerializer(many=True)})
    def get(self, request, pk):
        queryset = get_object_or_404(ProductFilterModel, pk=pk)
        serializer = FilterProductSerializer(queryset, context={'request': request, })
        return success_response(serializer.data)

    @swagger_auto_schema(request_body=FilterProductSerializer,
                         operation_description="Banners update",
                         tags=['Filter Product'],
                         responses={200: FilterProductSerializer(many=False)})
    def put(self, request, pk):
        valid_fields = {'title'}
        unexpected_fields = check_required_key(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        queryset = get_object_or_404(ProductFilterModel, pk=pk)
        serializer = FilterProductSerializer(instance=queryset, data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_response(serializer.data)
        return bad_request_response(serializer.errors)

    @swagger_auto_schema(operation_description="Delete a Banners",
                         tags=['Filter Product'],
                         responses={204: 'No content'})
    def delete(self, request, pk):
        queryset = get_object_or_404(ProductFilterModel, pk=pk)
        queryset.delete()
        return success_deleted_response("Successfully deleted")


class FilterProductsDetailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=ProductFilterProductSerializer,
                         operation_description="Banners product update",
                         tags=['Filter Product'],
                         responses={200: ProductFilterProductSerializer(many=False)})
    def put(self, request, pk):
        valid_fields = {'product_id'}
        unexpected_fields = check_required_key(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        queryset = get_object_or_404(ProductFilterProducts, pk=pk)
        serializer = ProductFilterProductSerializer(instance=queryset, data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_response(serializer.data)
        return bad_request_response(serializer.errors)

    @swagger_auto_schema(operation_description="Delete a Banners product",
                         tags=['Filter Product'],
                         responses={204: 'No content'})
    def delete(self, request, pk):
        queryset = get_object_or_404(ProductFilterProducts, pk=pk)
        queryset.delete()
        return success_deleted_response("Successfully deleted")
