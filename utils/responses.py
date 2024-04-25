from rest_framework import status
from rest_framework.response import Response


def bad_request_response(message):
    """
    Create a bad request response with the given error message.

    Args:
    - message (str): The error message to include in the response.

    Returns:
    - Response: A Response object with HTTP 400 Bad Request status.
    """
    return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)


def unauthorized_response(error_message):
    """
    Create an unauthorized response with the given error message.

    Args:
    - error_message (str): The error message to include in the response.

    Returns:
    - Response: A Response object with HTTP 401 Unauthorized status.
    """
    return Response({"error": error_message}, status=status.HTTP_401_UNAUTHORIZED)


def user_not_found_response(error_message):
    """
    Create a user not found response with the given error message.

    Args:
    - error_message (str): The error message to include in the response.

    Returns:
    - Response: A Response object with HTTP 404 Not Found status.
    """
    return Response({"error": error_message}, status=status.HTTP_404_NOT_FOUND)


def success_response(message):
    """
    Create a success response with the given message.

    Args:
    - message (str): The message to include in the response.

    Returns:
    - Response: A Response object with HTTP 200 OK status.
    """
    return Response(message, status=status.HTTP_200_OK)


def success_created_response(data):
    """
    Create a success response for a resource creation operation with the given data.

    Args:
    - data (dict): The data to include in the response.

    Returns:
    - Response: A Response object with HTTP 201 Created status.
    """
    return Response(data, status=status.HTTP_201_CREATED)


def success_deleted_response(message):
    """
    Create a success response for a resource deletion operation with the given message.

    Args:
    - message (str): The message to include in the response.

    Returns:
    - Response: A Response object with HTTP 204 No Content status.
    """
    return Response({'message': message}, status=status.HTTP_204_NO_CONTENT)
