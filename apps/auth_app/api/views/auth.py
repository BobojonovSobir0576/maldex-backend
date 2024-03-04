from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from apps.auth_app.api.serializers import (
    RegisterSerializer,
    InformationSerializer,
    LoginSerializer,
)
from utils.expected_fields import check_required_key
from utils.renderers import UserRenderers
from utils.responses import bad_request_response, success_created_response, success_response, success_deleted_response
from utils.token import get_token_for_user


class RegisterViews(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=RegisterSerializer,
                         operation_description="User create",
                         tags=['Sign Up'],
                         responses={201: RegisterSerializer(many=False)})
    def post(self, request):
        valid_fields = {"email", "first_name", "last_name", "username", "phone", "groups",
                        'about', 'photo', 'password', 'date_of_birth', 'city', 'gender', 'confirm_password'                        }
        unexpected_fields = check_required_key(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        serializer = RegisterSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user = serializer.instance
            token = get_token_for_user(user)
            return success_created_response(token)
        return bad_request_response(serializer.errors)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=LoginSerializer,
                         operation_description="User login",
                         tags=['Sign In'],
                         responses={201: LoginSerializer(many=False)})
    def post(self, request, *args, **kwargs):
        expected_fields = {"username", "password"}
        received_fields = set(request.data.keys())
        unexpected_fields = received_fields - expected_fields

        if unexpected_fields:
            return bad_request_response(
                f"Unexpected fields: {', '.join(unexpected_fields)}"
            )

        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        token = self.generate_user_token(user)

        return success_response(token)

    def get_serializer(self, *args, **kwargs):
        return LoginSerializer(*args, **kwargs)

    def generate_user_token(self, user):
        return get_token_for_user(user)


class ProfileViews(APIView):
    permission_classes = [AllowAny, IsAuthenticated]
    render_classes = [UserRenderers]

    @swagger_auto_schema(operation_description="Retrieve a user",
                         tags=['Profile'],
                         responses={200: InformationSerializer(many=True)})
    def get(self, request):
        serializer = InformationSerializer(request.user, context={'request': request})
        return success_response(serializer.data)

    @swagger_auto_schema(request_body=RegisterSerializer,
                         operation_description="User update",
                         tags=['Profile'],
                         responses={200: RegisterSerializer(many=False)})
    def put(self, request):
        valid_fields = {"first_name", "last_name", 'photo', 'about', 'phone', 'email'}
        unexpected_fields = check_required_key(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        serializer = RegisterSerializer(request.user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_response(serializer.data)
        return bad_request_response(serializer.errors)

    @swagger_auto_schema(operation_description="Delete a user",
                         tags=['Profile'],
                         responses={204: 'No content'})
    def delete(self, request):
        request.user.delete()
        return success_deleted_response("User deleted")
