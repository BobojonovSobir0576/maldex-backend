from django.db.models import Q
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers

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
        if not ('image' not in validated_data or validated_data['image']):
            raise ValidationError({"image": "not found"})
        color_name = self.context.pop('color', None)
        color_instance, created = Colors.objects.get_or_create(name=color_name)
        validated_data['colorID'] = color_instance
        return super().create(validated_data)


class CategoryListSerializers(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    """ Category create update and details """

    class Meta:
        model = ProductCategories
        fields = [
            'id', 'name', 'icon', 'logo', 'is_available'
        ]

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        super().update(instance, validated_data)
        print(validated_data, self.context)
        logo = self.context.get('logo') if self.context.get('logo') != 'null' else None
        icon = self.context.get('icon') if self.context.get('icon') != 'null' else None
        instance.logo = logo or instance.logo
        instance.icon = icon or instance.icon
        instance.save()
        return instance


class TertiaryCategorySerializer(serializers.ModelSerializer):
    """ Tertiary Category details """

    class Meta:
        model = TertiaryCategory
        fields = ['id', 'name']


class SubCategorySerializer(serializers.ModelSerializer):
    """ Sub Category details """
    children = serializers.SerializerMethodField(read_only=True)
    count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'children', 'count']

    def get_children(self, subcategory):
        children = TertiaryCategory.objects.filter(parent=subcategory)
        return TertiaryCategorySerializer(children, many=True).data

    def get_count(self, subcategory):
        products = Products.objects.filter(
            Q(categoryId=subcategory) |
            Q(categoryId__parent=subcategory) |
            Q(categoryId__parent__parent=subcategory)
        )
        return products.count()


class MainCategorySerializer(serializers.ModelSerializer):
    """ Main Category details """
    children = serializers.SerializerMethodField(read_only=True)
    name = serializers.CharField(required=False)

    class Meta:
        model = ProductCategories
        fields = ['id', 'parent', 'name', 'is_popular', 'is_hit', 'is_new', 'is_available', 'icon', 'logo', 'children']

    def get_children(self, category):
        children = SubCategory.objects.filter(parent=category)
        return SubCategorySerializer(children, many=True).data


class CategoryProductsSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField(read_only=True)
    children = SubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = ProductCategories
        fields = ['id', 'name', 'children', 'products']

    def get_products(self, category):
        products = Products.objects.filter(
            Q(categoryId=category) |
            Q(categoryId__parent=category) |
            Q(categoryId__parent__parent=category)
        )
        return ProductListSerializers(products[:6], many=True).data


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
    images_set = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Products
        fields = ['id', 'name', 'price', 'discount_price', 'images_set']

    def get_images_set(self, obj):
        images = obj.images_set.all()
        return [{
            'id': image.id,
            'image': self.context['request'].build_absolute_uri(image.image.url) if image.image else None,
            'image_url': image.image_url,
            'color': image.colorID.name
        } for image in images]

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class ProductDetailSerializers(serializers.ModelSerializer):
    """ Product details """
    images_set = serializers.SerializerMethodField(read_only=True)
    images = serializers.ListField(write_only=True, required=False)
    deleted_images = serializers.ListField(write_only=True, required=False)
    article = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    # categoryId = serializers.IntegerField(required=False, write_only=False)

    class Meta:
        model = Products  # Make sure to specify your model here
        fields = '__all__'

    def validate_categoryId(self, attrs):
        # print(attrs['categoryId'])
        print(attrs)
        return []

    def create(self, validated_data):
        images = validated_data.pop('images')
        product_instance = Products.objects.create(**validated_data)

        for image_data in images:
            print(image_data)
            image_data['productID'] = product_instance.id
            image_data['colorID'] = {
                'name': image_data['color']
            }
            image_serializer = ProductImageSerializer(data=image_data, context={'color': image_data['color'],
                                                                                'request': self.context['request']})
            if image_serializer.is_valid():
                image_serializer.save()
            else:
                raise ValueError(image_serializer.errors)

        return product_instance

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', [])
        for image_data in images_data:
            if image_data['image']:
                image_data['productID'] = instance.id
                image_data['colorID'] = {
                    'name': image_data['color']
                }
                image_serializer = ProductImageSerializer(data=image_data, context={'color': image_data['color'],
                                                                                    'request': self.context['request']})
                if image_serializer.is_valid():
                    image_serializer.save()
                else:
                    raise ValueError(image_serializer.errors)
        deleted_images = validated_data.pop('deleted_images', [])
        deleted_images = [] if deleted_images == [''] else deleted_images
        if deleted_images:
            ProductImage.objects.filter(productID=instance, id__in=deleted_images).delete()
        return super().update(instance, validated_data)

    def get_images_set(self, obj):
        images = obj.images_set.all()
        return [{
            'id': image.id,
            'image': self.context['request'].build_absolute_uri(image.image.url) if image.image else None,
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
