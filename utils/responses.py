from rest_framework import status
from rest_framework.response import Response


def bad_request_response(message):
    return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)


def unauthorized_response(error_message):
    return Response({"error": error_message}, status=status.HTTP_401_UNAUTHORIZED)


def user_not_found_response(error_message):
    return Response({"error": error_message}, status=status.HTTP_404_NOT_FOUND)


def success_response(message):
    return Response(message, status=status.HTTP_200_OK)


def success_created_response(data):
    return Response(data, status=status.HTTP_201_CREATED)


def success_deleted_response(message):
    return Response({'message': message}, status=status.HTTP_204_NO_CONTENT)