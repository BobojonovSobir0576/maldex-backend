from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from apps.blog.models import FAQ
from apps.product.models import *
from apps.product.proxy import *


class ColorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Colors
        fields = ['name', 'image']


class ProductImageSerializer(serializers.ModelSerializer):
    colorID = ColorSerializer(required=False)

    class Meta:
        model = ProductImage
        fields = '__all__'

    def create(self, validated_data):
        print(validated_data, self.context)
        color_name = self.context.pop('color', None)
        color_instance, created = Colors.objects.get_or_create(name=color_name)
        validated_data['colorID'] = color_instance
        return super().create(validated_data)


class CategoryListSerializers(serializers.ModelSerializer):
    """ Category create update and details """
    icon = serializers.ImageField(required=False)
    name = serializers.CharField(required=False)

    class Meta:
        model = ProductCategories
        fields = [
            'id', 'name', 'icon',
        ]

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class TertiaryCategorySerializer(serializers.ModelSerializer):
    """ Tertiary Category details """
    class Meta:
        model = ProductCategories
        fields = ['id', 'name', 'is_popular', 'is_hit', 'is_new', 'icon', 'logo']


class SubCategorySerializer(serializers.ModelSerializer):
    """ Sub Category details """
    children = TertiaryCategorySerializer(many=True, read_only=True)

    class Meta:
        model = ProductCategories
        fields = ['id', 'name', 'is_popular', 'is_hit', 'is_new', 'icon', 'logo', 'children']


class MainCategorySerializer(serializers.ModelSerializer):
    """ Main Category details """
    # children = SubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = ProductCategories
        fields = ['id', 'order', 'name', 'is_popular', 'is_hit', 'is_new', 'icon', 'logo']


class CategoryOrderSerializer(serializers.ModelSerializer):
    order = serializers.IntegerField(write_only=True)

    class Meta:
        model = ProductCategories
        fields = ['id', 'order']

    def update(self, instance, validated_data):
        order = validated_data.get('order', None)
        category2 = get_object_or_404(ProductCategories, order=validated_data['order'])

        instance.order, category2.order = order, instance.order
        validated_data['order'] = instance.order

        instance.save()
        category2.save()

        return super().update(instance, validated_data)


class ProductListSerializers(serializers.ModelSerializer):
    """ Product create update """
    # name = serializers.CharField(required=True)
    # price = serializers.FloatField(required=True)
    # price_type = serializers.CharField(max_length=25, required=True)
    # categoryId = serializers.IntegerField(allow_null=True, required=False)
    # images = serializers.ListSerializer(child=serializers.ImageField, required=False)

    class Meta:
        model = Products
        fields = '__all__'

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class ProductDetailSerializers(serializers.ModelSerializer):
    """ Product details """
    images_set = serializers.SerializerMethodField(read_only=True)
    images = serializers.ListField(write_only=True, required=False)

    class Meta:
        model = Products  # Make sure to specify your model here
        fields = '__all__'

    def create(self, validated_data):
        images = validated_data.pop('images')
        product_instance = Products.objects.create(**validated_data)

        for image_data in images:
            print(image_data['image'], image_data['color'])
            image_data['productID'] = product_instance.id
            image_data['colorID'] = {
                'name': image_data['color']
            }
            image_serializer = ProductImageSerializer(data=image_data, context={'color': image_data['color'], 'request': self.context['request']})      
            if image_serializer.is_valid():
                image_serializer.save() 
            else:
                raise ValueError(image_serializer.errors)

        return product_instance
    
    def get_images_set(self, obj):
        images = obj.images_set.all()
        return [{
            'image': self.context['request'].build_absolute_uri(image.image.url),
            'image_url': image.image_url,
            'color': image.colorID.name
            } for image in images]


class ProductJsonFileUploadCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(write_only=True, child=serializers.DictField(), required=False)
    category_name = serializers.CharField(write_only=True, allow_blank=True, required=False)
    images_set = ProductImageSerializer(read_only=True, many=True)

    class Meta:
        model = Products
        fields = [
            'id', 'name', 'brand', 'article', 'price', 'price_type',
            'categoryId', 'description', 'discount_price',
            'is_popular', 'is_hit', 'is_new', 'created_at', 'images', 'category_name', 'images_set'
        ]

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        category_name = validated_data.pop('category_name', None)

        if category_name:
            category, _ = ProductCategories.objects.get_or_create(name=category_name)
            validated_data['categoryId'] = category

        product = Products.objects.create(**validated_data)

        for image_data in images_data:
            ProductImage.objects.create(
                productID=product,
                big_url=image_data.get('big', ''),
                small_url=image_data.get('small', ''),
                superbig_url=image_data.get('superbig', ''),
                thumbnail_url=image_data.get('thumbnail', '')
            )

        return product
