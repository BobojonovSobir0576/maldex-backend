from msilib.schema import ListView

from django.shortcuts import get_object_or_404
from drf_yasg.openapi import Response
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView

from apps.blog.models import FAQ
from apps.product.api.serializers import FAQSerializer


class FAQListView(APIView):

    @swagger_auto_schema(operation_description='',
                         tags=['FAQ'],
                         responses={200: FAQSerializer(many=True)})
    def get(self, request):
        faq_type = request.query_params.get('type', None)
        faqs = FAQ.objects.filter(type=faq_type)
        serializer = FAQSerializer(faqs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description='Create a new FAQ',
                         tags=['FAQ'],
                         request_body=FAQSerializer,
                         responses={200: FAQSerializer})
    def post(self, request, *args, **kwargs):
        serializer = FAQSerializer(data=request.data, context={request: request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FAQDetailView(APIView):

    @swagger_auto_schema(operation_description='Get a FAQ',
                         tags=['FAQ'],
                         responses={200: FAQSerializer})
    def get(self, request, faq_id, *args, **kwargs):
        faq = get_object_or_404(FAQ, id=faq_id)
        serializer = FAQSerializer(faq)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description='Update a FAQ',
                         tags=['FAQ'],
                         request_body=FAQSerializer,
                         responses={200: FAQSerializer})
    def put(self, request, faq_id, *args, **kwargs):
        faq = get_object_or_404(FAQ, id=faq_id)
        serializer = FAQSerializer(faq, data=request.data, context={request: request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_description='Delete a FAQ',
                         tags=['FAQ'],)
    def delete(self, request, faq_id, *args, **kwargs):
        faq = get_object_or_404(FAQ, id=faq_id)
        faq.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)