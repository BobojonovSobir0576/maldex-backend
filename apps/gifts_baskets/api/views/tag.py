from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.gifts_baskets.api.serializers import TagSerializer
from apps.gifts_baskets.api.serializers import GiftBasketListSerializers, GiftBasketDetailSerializers
from apps.gifts_baskets.models import Tag, GiftsBaskets
from utils.expected_fields import check_required_key
from utils.responses import bad_request_response, success_created_response


class TagListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(tags=['Gifts Baskets'],
                         responses={200: TagSerializer(many=True)})
    def get(self, request):
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class GiftBasketListByTagView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(operation_description="Retrieve a list of gift baskets",
                         tags=['Gifts Baskets'],
                         responses={200: GiftBasketListSerializers(many=True)})
    def get(self, request, tag_id):
        queryset = GiftsBaskets.objects.all().order_by('-id').filter(tags__id=tag_id)
        serializer = GiftBasketDetailSerializers(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
