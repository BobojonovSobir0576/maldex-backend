from django.http import JsonResponse
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils.deprecation import MiddlewareMixin
from django.middleware.csrf import CsrfViewMiddleware
from django.conf import settings
import requests


class JsonErrorResponseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        error_message = str(exception)
        response_data = {"error": error_message}
        return JsonResponse(response_data, status=500)


class Custom404Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response is None:
            return self.handle_404(request)

        if response.status_code == status.HTTP_404_NOT_FOUND:
            return self.handle_404(request)

        return response

    def handle_404(self, request):
        data = {"dateil": "Page not Found"}
        return JsonResponse(data, status=status.HTTP_404_NOT_FOUND)


class SimpleJWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if any(map(request.path.startswith, ('/admin/', '/static/', '/media/', '/auth/', '/docs/', '/schema/', '/swagger/', '/redoc/',
                                             '/team/', '/category/', '/categories/', '/cities/', '/city/', '/countries/', '/country/'))):
            return self.get_response(request)
        jwt_auth = JWTAuthentication()
        try:
            validated_token = jwt_auth.get_validated_token(request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1])
            request.user = jwt_auth.get_user(validated_token)
        except Exception as e:

            return JsonResponse({'error': 'User is not authentication'}, status=401)

        return self.get_response(request)


class DisableCSRFOnAPI(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith('/auth/social-media/'):  # Adjust the path according to your API endpoint
            setattr(request, '_dont_enforce_csrf_checks', True)