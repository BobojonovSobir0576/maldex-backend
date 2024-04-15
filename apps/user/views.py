from drf_yasg.utils import swagger_auto_schema

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from apps.user.models import User
from apps.user.serializers import UserSerializer, RegisterSerializer, LoginSerializer


class UserListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={200: UserSerializer(many=True)},
        tags=['User']
    )
    def get(self, request):
        queryset = User.objects.all()
        serializer = UserSerializer(queryset, context={'request': request}, many=True)
        return Response(serializer.data, status=200)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: UserSerializer()},
        tags=['User']
    )
    def get(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data, status=200)


class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    @swagger_auto_schema(
        tags=['Auth'],
        request_body=LoginSerializer(),
        responses={201: 'Tokens'}
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['Auth'],
        request_body=RegisterSerializer(),
        responses={200: UserSerializer()}
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)
