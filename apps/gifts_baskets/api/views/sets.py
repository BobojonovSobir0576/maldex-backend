from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.responses import (
    bad_request_response,
    success_response,
    success_created_response,
    success_deleted_response,
)
from utils.expected_fields import check_required_key
from drf_yasg.utils import swagger_auto_schema
from apps.gifts_baskets.api.serializers import *


class SetCategoryListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(operation_description="Retrieve a list of set catalog",
                         tags=['Sets catalog list'],
                         responses={200: SetCategoryListSerializer(many=True)})
    def get(self, request):
        queryset = SetCategory.objects.all().order_by('-id')
        serializer = SetCategoryListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=SetCategoryListSerializer,
                         operation_description="Set catalog create",
                         tags=['Sets catalog list'],
                         responses={201: SetCategoryListSerializer(many=False)})
    def post(self, request):
        valid_fields = {'title', 'is_available', 'product_data'}
        unexpected_fields = check_required_key(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")
        serializer = SetCategoryListSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_created_response(serializer.data)
        return bad_request_response(serializer.errors)


class SetCatalogDetailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(operation_description="Retrieve set catalog",
                         tags=['Sets catalog list'],
                         responses={200: SetCategoryListSerializer(many=True)})
    def get(self, request, pk):
        queryset = get_object_or_404(SetCategory, pk=pk)
        serializer = SetCategoryListSerializer(queryset, context={'request': request, })
        return success_response(serializer.data)

    """ Category Put View """

    @swagger_auto_schema(request_body=SetCategoryListSerializer,
                         operation_description="Set catalog update",
                         tags=['Sets catalog list'],
                         responses={200: SetCategoryListSerializer(many=False)})
    def put(self, request, pk):
        valid_fields = {'title', 'is_available'}
        unexpected_fields = check_required_key(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        queryset = get_object_or_404(SetCategory, pk=pk)
        serializer = SetCategoryListSerializer(instance=queryset, data=request.data,
                                               context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_response(serializer.data)
        return bad_request_response(serializer.errors)

    """ Category Delete View """

    @swagger_auto_schema(operation_description="Delete a set catalog",
                         tags=['Sets catalog list'],
                         responses={204: 'No content'})
    def delete(self, request, pk):
        queryset = get_object_or_404(SetCategory, pk=pk)
        queryset.delete()
        return success_deleted_response("Successfully deleted")


class SetProductDetailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=SetProductListSerializer,
                         operation_description="Set product update",
                         tags=['Sets product list'],
                         responses={200: SetProductListSerializer(many=False)})
    def put(self, request, pk):
        valid_fields = {'product_sets', 'quantity'}
        unexpected_fields = check_required_key(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        queryset = get_object_or_404(SetProducts, pk=pk)
        serializer = SetProductListSerializer(instance=queryset, data=request.data,
                                              context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_response(serializer.data)
        return bad_request_response(serializer.errors)

    @swagger_auto_schema(operation_description="Delete a set product",
                         tags=['Sets product list'],
                         responses={204: 'No content'})
    def delete(self, request, pk):
        queryset = get_object_or_404(SetProducts, pk=pk)
        queryset.delete()
        return success_deleted_response("Successfully deleted")
