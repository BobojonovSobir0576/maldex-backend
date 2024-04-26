from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


from apps.gifts_baskets.api.serializers import *
from apps.gifts_baskets.models import *
from utils.expected_fields import check_required_key
from utils.responses import bad_request_response, success_created_response, success_response, success_deleted_response
from drf_yasg import openapi


class TagCategoryListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(operation_description="Retrieve a list of tag categories",
                         tags=['Tag Categories'],
                         responses={200: CategoryTagListSerializer(many=True)})
    def get(self, request):
        queryset = TagCategory.objects.all()
        serializer = CategoryTagListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=CategoryTagListSerializer,
                         operation_description="Gifts Baskets Categories create",
                         tags=['Tag Categories'],
                         responses={201: CategoryTagListSerializer(many=False)})
    def post(self, request):
        valid_fields = {'name', 'parent', 'is_available'}
        unexpected_fields = check_required_key(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        serializer = CategoryTagListSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_created_response(serializer.data)
        return bad_request_response(serializer.errors)


class TagCategoryDetailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(operation_description="Retrieve tag category",
                         tags=['Tag Categories'],
                         responses={200: CategoryTagListSerializer(many=True)})
    def get(self, request, pk):
        queryset = get_object_or_404(TagCategory, pk=pk)
        serializer = CategoryTagListSerializer(queryset, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    """ Category Put View """

    @swagger_auto_schema(request_body=CategoryTagListSerializer,
                         operation_description="Tag Categories update",
                         tags=['Tag Categories'],
                         responses={200: CategoryTagListSerializer(many=False)})
    def put(self, request, pk):
        valid_fields = {'name', 'parent', 'is_available'}
        unexpected_fields = check_required_key(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        queryset = get_object_or_404(TagCategory, pk=pk)
        serializer = CategoryTagListSerializer(instance=queryset, data=request.data,
                                                      context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_response(serializer.data)
        return bad_request_response(serializer.errors)

    """ Category Delete View """

    @swagger_auto_schema(operation_description="Delete a tag category",
                         tags=['Tag Categories'],
                         responses={204: 'No content'})
    def delete(self, request, pk):
        queryset = get_object_or_404(TagCategory, pk=pk)
        queryset.delete()
        return success_deleted_response("Successfully deleted")


class TagListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(tags=['Basket Tag'],
                         responses={200: TagSerializer(many=True)})
    def get(self, request):
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=['Basket Tag'],
                         responses={200: TagSerializer},
                         request_body=TagSerializer)
    def post(self, request):
        serializer = TagSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_created_response(serializer.data)
        return bad_request_response(serializer.errors)


class TagDetailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(operation_description="Retrieve tag category",
                         tags=['Basket Tag'],
                         responses={200: TagSerializer(many=True)})
    def get(self, request, pk):
        queryset = get_object_or_404(Tag, pk=pk)
        serializer = TagSerializer(queryset, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    """ Category Put View """

    @swagger_auto_schema(request_body=TagSerializer,
                         operation_description="Tag Categories update",
                         tags=['Basket Tag'],
                         responses={200: TagSerializer(many=False)})
    def put(self, request, pk):
        valid_fields = {'name', 'order', 'tag_category'}
        unexpected_fields = check_required_key(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        queryset = get_object_or_404(Tag, pk=pk)
        serializer = TagSerializer(instance=queryset, data=request.data,
                                               context={'request': request})
        print(request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_response(serializer.data)
        return bad_request_response(serializer.errors)

    """ Category Delete View """

    @swagger_auto_schema(operation_description="Delete a tag category",
                         tags=['Basket Tag'],
                         responses={204: 'No content'})
    def delete(self, request, pk):
        queryset = get_object_or_404(Tag, pk=pk)
        queryset.delete()
        return success_deleted_response("Successfully deleted")


class GiftBasketListByTagView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(operation_description="Retrieve a list of gift baskets",
                         tags=['Basket Tag'],
                         responses={200: GiftBasketListSerializers(many=True)})
    def get(self, request, tag_id):
        queryset = GiftsBaskets.objects.all().order_by('-id').filter(tags__id=tag_id)
        serializer = GiftBasketDetailSerializers(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
