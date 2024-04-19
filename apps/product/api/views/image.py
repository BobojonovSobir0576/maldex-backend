from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from drf_yasg import openapi

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser

from apps.product.filters import ProductFilter
from apps.product.models import *
from apps.product.api.serializers import ProductDetailSerializers, SubCategorySerializer, \
    TertiaryCategorySerializer
from apps.product.proxy import TertiaryCategory, SubCategory
from utils.responses import (
    bad_request_response,
    success_response,
    success_deleted_response,
)

from utils.pagination import PaginationMethod, StandardResultsSetPagination
from drf_yasg.utils import swagger_auto_schema


class ProductImageView(APIView):

    @swagger_auto_schema(operation_description="Delete a Products",
                         tags=['Product Image'],
                         responses={204: 'No content'})
    def delete(self, request, image_id):
        image = get_object_or_404(ProductImage, pk=image_id)
        image.delete()
        print('ishladi DELETE')
        return success_deleted_response("Successfully deleted")
