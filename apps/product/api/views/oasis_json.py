import json
from django.db import transaction
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.product.api.serializers import (
    ProductJsonFileUploadCreateSerializer
)

from drf_yasg.utils import swagger_auto_schema


class ProductUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    file_parameter = openapi.Parameter(
        'file', in_=openapi.IN_FORM, description="Upload JSON file to add products to the database",
        type=openapi.TYPE_FILE
    )

    @swagger_auto_schema(
        manual_parameters=[file_parameter],
        operation_description="Add products from a JSON file",
        tags=['Products'],
        responses={201: "Products uploaded successfully"}
    )
    def post(self, request, *args, **kwargs):
        file_obj = request.data.get('file')
        if file_obj is None:
            return Response({'error': 'A file is required.'}, status=400)

        try:
            products_data = json.loads(file_obj.read().decode('utf-8'))
            if not isinstance(products_data, list):
                products_data = [products_data]  # Ensure it's a list for consistency
        except json.JSONDecodeError:
            return Response({'error': 'The file contains invalid JSON.'}, status=400)

        with transaction.atomic():
            created_products, errors = self.process_products(products_data)

        if errors:
            return Response({'errors': errors}, status=400)
        return Response({'message': f'{len(created_products)} products uploaded successfully'}, status=201)

    def process_products(self, products_data):
        """
        Validates product data and creates product instances.

        :param products_data: List of dictionaries containing product data
        :return: Tuple containing lists of created product instances and errors
        """
        created_products = []
        errors = []

        for data in products_data:
            serializer = ProductJsonFileUploadCreateSerializer(data=data)
            if serializer.is_valid():
                created_product = serializer.save()
                created_products.append(created_product)
            else:
                errors.append(serializer.errors)

        return created_products, errors
