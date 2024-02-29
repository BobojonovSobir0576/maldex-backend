from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from apps.product.models import *


class CategoryListSerializers(serializers.ModelSerializer):
    """ Category create update and details """
    icon = serializers.ImageField(required=False)
    name = serializers.CharField(required=True)
    subcategory = serializers.IntegerField(allow_null=True, required=False)

    class Meta:
        model = ProductCategories
        fields = [
            'id', 'name', 'subcategory', 'icon',
        ]

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class ProductListSerializers(serializers.ModelSerializer):
    """ Product create update """
    image = serializers.ImageField(required=False)
    name = serializers.CharField(required=True)
    price = serializers.FloatField(required=True)
    price_type = serializers.CharField(max_length=25, required=True)
    categoryId = serializers.IntegerField(allow_null=True, required=False)
    content = serializers.CharField(required=True)

    class Meta:
        model = Products
        fields = [
            'id', 'name', 'content', 'image', 'price', 'price_type', 'categoryId', 'created_at'
        ]

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class ProductDetailSerializers(serializers.ModelSerializer):
    """ Product details """

    class Meta:
        model = Products
        fields = [
            'id', 'name', 'content', 'image', 'price', 'price_type', 'categoryId', 'created_at'
        ]