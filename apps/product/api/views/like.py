from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.product.api.serializers import ProductListSerializers
from apps.product.models import Products, Like


class ProductsLikeView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_description="Like product",
                         tags=['Like'],
                         responses={200: None})
    def post(self, request, product_id):
        user = request.user
        product = get_object_or_404(Products, id=product_id)
        like, _ = Like.objects.get_or_create(user=user, product=product)
        return Response({'message': 'liked'}, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description="Delete like product",
                         tags=['Like'],
                         responses={204: None})
    def delete(self, request, product_id):
        user = request.user
        product = get_object_or_404(Products, id=product_id)
        like = get_object_or_404(Like, user=user, product=product)
        like.delete()
        return Response({'message': 'deleted'}, status=status.HTTP_204_NO_CONTENT)


class LikedProductsView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_description="Get liked products",
                         tags=['User'],
                         responses={200: None})
    def get(self, request):
        user = request.user
        liked_products = Products.objects.filter(likes__user=user)
        serializer = ProductListSerializers(liked_products, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
