from django.db import transaction
from django.db.models import Q, Count
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
        fields = ['id', 'name', 'parent', 'icon', 'logo', 'is_available', 'is_popular',
                  'is_hit',  'is_new', 'order', 'created_at', 'updated_at', 'site']


    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        order = validated_data.pop('order', None)
        print(order)
        logo = self.context.get('logo') if self.context.get('logo') != 'null' else None
        icon = self.context.get('icon') if self.context.get('icon') != 'null' else None
        instance.logo = logo or instance.logo
        instance.icon = icon or instance.icon
        instance.is_popular = validated_data.pop('is_popular', instance.is_popular)
        instance.is_hit = validated_data.pop('is_hit', instance.is_popular)
        instance.is_new = validated_data.pop('is_new', instance.is_popular)
        if order:
            instance.order = int(order)
        instance.save()
        instance.save()
        return instance


class TertiaryCategorySerializer(serializers.ModelSerializer):
    """ Tertiary Category details """

    class Meta:
        model = TertiaryCategory
        fields = ['id', 'name', 'site']


class SubCategorySerializer(serializers.ModelSerializer):
    """ Sub Category details """

    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'site']


class SubCategoryWithCountSerializer(serializers.ModelSerializer):
    """ Sub Category with Count details """
    count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'count']

    def get_count(self, subcategory):
        return Products.objects.prefetch_related('categoryId').select_related('categoryId').filter(
            Q(categoryId=subcategory) | Q(categoryId__parent=subcategory)
        ).aggregate(total=Count('id'))['total'] or 0


class MainCategorySerializer(serializers.ModelSerializer):
    """ Main Category details """
    children = serializers.SerializerMethodField(read_only=True)
    name = serializers.CharField(required=False)

    class Meta:
        model = ProductCategories
        fields = ['id', 'parent', 'name', 'is_popular', 'is_hit', 'is_new', 'is_available',
                  'order', 'icon', 'logo', 'children', 'created_at', 'updated_at', 'site']

    def get_children(self, category):
        children = category.children
        return SubCategorySerializer(children, many=True).data


class CategoryProductsSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField(read_only=True)
    children = SubCategoryWithCountSerializer(many=True, read_only=True)

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

    # categoryId = serializers.IntegerField(required=False)

    class Meta:
        model = Products  # Make sure to specify your model here
        fields = '__all__'

    # def validate_categoryId(self, attrs):
    #     # print(attrs['categoryId'])
    #     print(attrs)
    #     return []

    def create(self, validated_data):
        images = validated_data.pop('images')
        print(validated_data)
        product_instance = Products.objects.create(**validated_data)
        print(product_instance)

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


class ExternalCategoryListSerializer(serializers.ModelSerializer):
    category = CategoryListSerializers(read_only=True)

    class Meta:
        model = ExternalCategory
        fields = '__all__'


class CategoryAutoUploaderSerializer(serializers.ModelSerializer):
    external_id = serializers.IntegerField(required=False)
    parent_id = serializers.IntegerField(write_only=True, required=False)
    name = serializers.CharField(max_length=255, required=False)

    class Meta:
        model = ProductCategories
        fields = [
            'id', 'name', 'parent', 'external_id', 'parent_id', 'site',
        ]

    def create(self, validated_data):
        external_id = validated_data.pop('external_id', None)
        parent_id = validated_data.pop('parent_id', None)
        name = validated_data['name']

        category = ProductCategories.objects.filter(external_categories__external_id=external_id).first()
        parent_category = ProductCategories.objects.filter(external_categories__external_id__in=[parent_id]).first()

        new_category = None

        if not category:
            try:
                is_4_level = parent_category.parent.parent is not None
            except:

                is_4_level = False
            if not is_4_level:
                new_category = ProductCategories.objects.create(name=name, parent=parent_category, site=validated_data.get('site', None))
                ExternalCategory.objects.create(external_id=external_id, category=new_category)
            else:
                ExternalCategory.objects.create(external_id=external_id, category=parent_category)

        return category or new_category or parent_category


class ProductAutoUploaderSerializer(serializers.ModelSerializer):
    color_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    image_set = serializers.JSONField(required=False)
    categoryId = serializers.IntegerField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = Products
        fields = [
            'id', 'name', 'code', 'article', 'product_size', 'material', 'description', 'brand', 'price',
            'price_type', 'discount_price', 'weight', 'barcode', 'ondemand', 'moq', 'days', 'pack', 'prints',
            'created_at', 'updated_at', 'color_name', 'image_set', 'categoryId', 'quantity', 'site'
        ]

    def check_color_exists(self, color_name):
        if color_name:
            color, _ = Colors.objects.get_or_create(name=color_name)
            return color
        return None

    def create_img_into_product(self, img_set, color_instance, product_instance):
        for img in img_set:
            ProductImage.objects.create(
                productID=product_instance,
                colorID=color_instance,
                image_url=img['name']
            )

    def get_category_instance(self, cate_id):
        if cate_id is not None:
            external_category = ExternalCategory.objects.filter(external_id=cate_id).first()
            if external_category and external_category.category:
                return external_category.category
        return None

    @transaction.atomic
    def create(self, validated_data):
        color_name = validated_data.pop('color_name', None)
        image_set = validated_data.pop('image_set', [])
        categoryId = validated_data.pop('categoryId', None)

        color_instance = self.check_color_exists(color_name)
        category_instance = self.get_category_instance(categoryId)

        # Since you are only creating a single product instance, unpacking is appropriate
        product_instance, created = Products.objects.get_or_create(**validated_data)

        if category_instance:
            product_instance.categoryId = category_instance
            product_instance.save()

        if image_set:
            self.create_img_into_product(image_set, color_instance, product_instance)

        return product_instance


class ProductAutoUploaderDetailSerializer(serializers.ModelSerializer):
    price = serializers.FloatField()
    discount_price = serializers.FloatField()
    quantity = serializers.FloatField()

    class Meta:
        model = Products
        fields = [
            'id', 'name', 'code', 'article', 'product_size', 'material', 'description', 'brand', 'price',
            'price_type', 'discount_price', 'weight', 'barcode', 'ondemand', 'moq', 'days', 'pack', 'prints',
            'created_at', 'updated_at', 'categoryId', 'quantity'
        ]

    def update(self, instance, validated_data):
        # Update the instance fields with new values from validated_data or use existing if not provided
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.price = validated_data.get('price', instance.price)
        instance.discount_price = validated_data.get('discount_price', instance.discount_price)

        # Save the updated instance
        instance.save()

        return instance
