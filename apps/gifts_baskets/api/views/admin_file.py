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


class AdminFilesListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(operation_description="Retrieve a list of admin files",
                         tags=['Admin files list'],
                         responses={200: AdminFilesListSerializer(many=True)})
    def get(self, request):
        queryset = AdminFiles.objects.all()
        serializer = AdminFilesListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=AdminFilesListSerializer,
                         operation_description="Admin files create",
                         tags=['Admin files list'],
                         responses={201: AdminFilesListSerializer(many=False)})
    def post(self, request):
        valid_fields = {'name', 'file'}
        unexpected_fields = check_required_key(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        serializer = AdminFilesListSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save(file=request.FILES.get('file'))
            return success_created_response(serializer.data)
        return bad_request_response(serializer.errors)


class AdminFilesDetailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(operation_description="Retrieve admin files",
                         tags=['Admin files list'],
                         responses={200: AdminFilesListSerializer(many=True)})
    def get(self, request, pk):
        queryset = get_object_or_404(AdminFiles, pk=pk)
        serializer = AdminFilesListSerializer(queryset, context={'request': request, })
        return success_response(serializer.data)

    """ Category Put View """

    @swagger_auto_schema(request_body=AdminFilesListSerializer,
                         operation_description="Admin files update",
                         tags=['Admin files list'],
                         responses={200: AdminFilesListSerializer(many=False)})
    def put(self, request, pk):
        valid_fields = {'name', 'file'}
        unexpected_fields = check_required_key(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        queryset = get_object_or_404(AdminFiles, pk=pk)
        serializer = AdminFilesListSerializer(instance=queryset, data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_response(serializer.data)
        return bad_request_response(serializer.errors)

    """ Category Delete View """

    @swagger_auto_schema(operation_description="Delete a admin files",
                         tags=['Admin files list'],
                         responses={204: 'No content'})
    def delete(self, request, pk):
        queryset = get_object_or_404(AdminFiles, pk=pk)
        queryset.delete()
        return success_deleted_response("Successfully deleted")
