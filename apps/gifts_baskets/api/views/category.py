from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.pagination import StandardResultsSetPagination

from utils.responses import (
    bad_request_response,
    success_response,
    success_created_response,
    success_deleted_response,
)
from utils.pagination import PaginationMethod
from utils.expected_fields import check_required_key
from drf_yasg.utils import swagger_auto_schema
from apps.gifts_baskets.api.serializers import *


class GiftBasketCategoryListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(operation_description="Retrieve a list of categories",
                         tags=['Gifts Baskets Categories'],
                         responses={200: GiftBasketCategoryDetailSerializers(many=True)})
    def get(self, request):
        queryset = GiftsBasketCategory.objects.filter(
            parent__isnull=True,
            is_available=True
        )
        serializer = GiftBasketCategoryDetailSerializers(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=GiftBasketCategoryListSerializer,
                         operation_description="Gifts Baskets Categories create",
                         tags=['Gifts Baskets Categories'],
                         responses={201: GiftBasketCategoryListSerializer(many=False)})
    def post(self, request):
        valid_fields = {'name', 'parent', 'is_available'}
        unexpected_fields = check_required_key(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        serializers = GiftBasketCategoryListSerializer(data=request.data, context={'request': request})
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return success_created_response(serializers.data)
        return bad_request_response(serializers.errors)


class GiftBasketCategoryDetailView(APIView, PaginationMethod):
    permission_classes = [AllowAny]
    """ Category Get View """

    @swagger_auto_schema(operation_description="Retrieve gift basket category or sub categories",
                         tags=['Gifts Baskets Categories'],
                         responses={200: GiftBasketCategoryDetailSerializers(many=True)})
    def get(self, request, pk):
        queryset = get_object_or_404(GiftsBasketCategory, pk=pk)
        serializers = GiftBasketCategoryDetailSerializers(queryset, context={'request': request, })
        return success_response(serializers.data)

    """ Category Put View """

    @swagger_auto_schema(request_body=GiftBasketCategoryListSerializer,
                         operation_description="Gifts Baskets Categories update",
                         tags=['Gifts Baskets Categories'],
                         responses={200: GiftBasketCategoryListSerializer(many=False)})
    def put(self, request, pk):
        valid_fields = {'name', 'parent', 'is_available'}
        unexpected_fields = check_required_key(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        queryset = get_object_or_404(GiftsBasketCategory, pk=pk)
        serializers = GiftBasketCategoryListSerializer(instance=queryset, data=request.data,
                                              context={'request': request})
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return success_response(serializers.data)
        return bad_request_response(serializers.errors)

    """ Category Delete View """

    @swagger_auto_schema(operation_description="Delete a gift basket category",
                         tags=['Gifts Baskets Categories'],
                         responses={204: 'No content'})
    def delete(self, request, pk):
        queryset = get_object_or_404(GiftsBasketCategory, pk=pk)
        queryset.delete()
        return success_deleted_response("Successfully deleted")