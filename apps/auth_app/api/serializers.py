from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


from apps.auth_app.models import (
    CustomUser,
)


class IncorrectCredentialsError(serializers.ValidationError):
    pass


class UnverifiedAccountError(serializers.ValidationError):
    pass


class GroupsSerializers(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ['id', 'name']


class BaseUserSerializer(serializers.ModelSerializer):
    phone = serializers.EmailField(validators=[UniqueValidator(queryset=CustomUser.objects.all())])
    groups = GroupsSerializers(read_only=True, many=True)

    class Meta:
        model = get_user_model()
        fields = ["id", "email", "first_name", "last_name", "username", "phone", "groups",]


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=30, required=True,
                                     validators=[UniqueValidator(queryset=CustomUser.objects.all())])
    email = serializers.CharField(max_length=30, required=True,
                                  validators=[UniqueValidator(queryset=CustomUser.objects.all())])
    phone = serializers.CharField(max_length=30, required=True,
                                  validators=[UniqueValidator(queryset=CustomUser.objects.all())])
    photo = serializers.ImageField(required=False)
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ['about', 'photo', 'password', 'date_of_birth', 'gender',
                                                   'confirm_password']
        extra_kwargs = {
            "password": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
            "date_of_birth": {"required": True},
            "about": {"required": True},
            "gender": {"required": True},
            "photo": {"required": True},
        }

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as exc:
            raise serializers.ValidationError(str(exc))
        return value

    def create(self, validated_data):
        self.validate_password_match(validated_data)
        validated_data.pop("confirm_password")
        user = self.create_user(validated_data)
        self.add_user_to_role(user)
        return user

    def validate_password_match(self, validated_data):
        if validated_data["password"] != validated_data["confirm_password"]:
            raise serializers.ValidationError({"error": "Passwords don't match"})

    def create_user(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def add_user_to_role(self, user):
        try:
            role = Group.objects.get(name='user')
            user.groups.add(role)
            user.is_staff = False
            user.save()
        except ObjectDoesNotExist:
            raise serializers.ValidationError({"error": "Invalid role"})


class InformationSerializer(BaseUserSerializer):

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ['about', 'photo', 'password', 'date_of_birth', 'gender',
                                                   'date_joined']


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=50, min_length=2)
    password = serializers.CharField(max_length=50, min_length=1)

    class Meta:
        model = get_user_model()
        fields = ("username", "password")

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")
        user = self.authenticate_user(username, password)

        self.validate_user(user)

        data["user"] = user
        data['password'] = password
        return data

    def authenticate_user(self, username, password):
        user = authenticate(username=username, password=password)
        return user

    def validate_user(self, user):
        if not user or not user.is_active:
            raise IncorrectCredentialsError({"error": "Incorrect phone or password"})
