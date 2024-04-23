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
from utils.pagination import PaginationMethod
from utils.expected_fields import check_required_key
from drf_yasg.utils import swagger_auto_schema
from apps.gifts_baskets.api.serializers import *


class GiftBasketListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(operation_description="Retrieve a list of gift baskets",
                         tags=['Gifts Baskets'],
                         responses={200: GiftBasketListSerializers(many=True)})
    def get(self, request):
        queryset = GiftsBaskets.objects.all().order_by('-id')
        serializer = GiftBasketDetailSerializers(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=GiftBasketListSerializers,
                         operation_description="Gifts Baskets create",
                         tags=['Gifts Baskets'],
                         responses={201: GiftBasketListSerializers(many=False)})
    def post(self, request):
        valid_fields = {'title', 'description', 'other_sets', 'images_data', 'category_data', 'products_data',
                        'article', 'discount_price', 'price_type', 'price', 'price_set', 'tags'}
        unexpected_fields = check_required_key(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        serializer = GiftBasketListSerializers(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_created_response(serializer.data)
        return bad_request_response(serializer.errors)


class GiftBasketDetailView(APIView, PaginationMethod):
    permission_classes = [AllowAny]

    @swagger_auto_schema(operation_description="Retrieve gift basket",
                         tags=['Gifts Baskets'],
                         responses={200: GiftBasketListSerializers(many=True)})
    def get(self, request, pk):
        queryset = get_object_or_404(GiftsBaskets, pk=pk)
        serializer = GiftBasketDetailSerializers(queryset, context={'request': request, })
        return success_response(serializer.data)

    """ Category Put View """

    @swagger_auto_schema(request_body=GiftBasketListSerializers,
                         operation_description="Gifts Baskets update",
                         tags=['Gifts Baskets'],
                         responses={200: GiftBasketListSerializers(many=False)})
    def put(self, request, pk):
        valid_fields = {'name', 'parent', 'is_available'}
        unexpected_fields = check_required_key(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        queryset = get_object_or_404(GiftsBaskets, pk=pk)
        serializer = GiftBasketListSerializers(instance=queryset, data=request.data,
                                               context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_response(serializer.data)
        return bad_request_response(serializer.errors)

    """ Category Delete View """

    @swagger_auto_schema(operation_description="Delete a gift basket",
                         tags=['Gifts Baskets'],
                         responses={204: 'No content'})
    def delete(self, request, pk):
        queryset = get_object_or_404(GiftsBaskets, pk=pk)
        queryset.delete()
        return success_deleted_response("Successfully deleted")


class GiftsBasketProductDetailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=GiftsBasketProductDetailsSerializers,
                         operation_description="Gifts Baskets product quantity to change",
                         tags=['Gifts Baskets Product'],
                         responses={200: GiftsBasketProductDetailsSerializers(many=False)})
    def put(self, request, pk):
        valid_fields = {'quantity', }
        unexpected_fields = check_required_key(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        queryset = get_object_or_404(GiftsBasketProduct, pk=pk)
        serializer = GiftsBasketProductDetailsSerializers(instance=queryset, data=request.data,
                                                          context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_response(serializer.data)
        return bad_request_response(serializer.errors)

    @swagger_auto_schema(operation_description="Delete a gift basket product",
                         tags=['Gifts Baskets Product'],
                         responses={204: 'No content'})
    def delete(self, request, pk):
        queryset = get_object_or_404(GiftsBasketProduct, pk=pk)
        queryset.delete()
        return success_deleted_response("Successfully deleted")


class GiftsBasketImageDetailSerializers(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=GiftsBasketImagesSerializers,
                         operation_description="Gifts Baskets image update",
                         tags=['Gifts Baskets Image'],
                         responses={200: GiftsBasketImagesSerializers(many=False)})
    def put(self, request, pk):
        valid_fields = {'image', }
        unexpected_fields = check_required_key(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        queryset = get_object_or_404(GiftsBasketImages, pk=pk)
        serializer = GiftsBasketImagesSerializers(instance=queryset, data=request.data,
                                                  context={'request': request,
                                                           'image': request.FILES.get('image', None)})

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_response(serializer.data)
        return bad_request_response(serializer.errors)

    @swagger_auto_schema(operation_description="Delete a gift basket image",
                         tags=['Gifts Baskets Image'],
                         responses={204: 'No content'})
    def delete(self, request, pk):
        queryset = get_object_or_404(GiftsBasketImages, pk=pk)
        queryset.delete()
        return success_deleted_response("Successfully deleted")
