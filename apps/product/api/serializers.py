import os
import time

import requests
from django.db import transaction
from django.db.models import Q, Count
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from apps.gifts_baskets.models import GiftsBasketCategory, GiftsBaskets
from apps.product.api.access import get_data
from apps.product.models import *
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
    is_available = serializers.BooleanField(required=False)
    """ Category create update and details """

    class Meta:
        model = ProductCategories
        fields = ['id', 'name', 'parent', 'icon', 'logo', 'is_available', 'is_popular',
                  'is_hit', 'is_new', 'order', 'order_top', 'created_at', 'updated_at', 'site']

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        logo = self.context.get('logo') if self.context.get('logo') != 'null' else None
        icon = self.context.get('icon') if self.context.get('icon') != 'null' else None
        instance.logo = logo or instance.logo
        instance.icon = icon or instance.icon
        instance.order_top = validated_data.get('order_top', instance.order_top)
        instance.order = validated_data.get('order', instance.order_top)
        instance.name = validated_data.get('name', instance.name)
        instance.parent = validated_data.get('parent', instance.parent)
        instance.is_popular = validated_data.get('is_popular', instance.is_popular)
        instance.is_hit = validated_data.get('is_hit', instance.is_hit)
        instance.is_new = validated_data.get('is_new', instance.is_new)
        instance.is_available = validated_data.get('is_available', instance.is_available)

        instance.save()
        return instance


class TertiaryCategorySerializer(serializers.ModelSerializer):
    """ Tertiary Category details """
    count = serializers.SerializerMethodField()

    class Meta:
        model = TertiaryCategory
        fields = ['id', 'name', 'count', 'site']

    @staticmethod
    def get_count(category):
        return category.products.all().count()


class SubCategorySerializer(serializers.ModelSerializer):
    children = TertiaryCategorySerializer(read_only=True, many=True)
    count = serializers.SerializerMethodField()
    """ Sub Category details """

    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'count', 'children', 'site']

    @staticmethod
    def get_count(category):
        category_ids = [category.id] + list(category.children.values_list('id', flat=True))
        descendants_query = Q(categoryId__in=category_ids)
        count = Products.objects.filter(descendants_query).aggregate(total_count=Count('id'))['total_count'] or 0

        return count


class SubCategoryWithCountSerializer(serializers.ModelSerializer):
    """ Sub Category with Count details """
    count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'count']

    @staticmethod
    def get_count(subcategory):
        return Products.objects.prefetch_related('categoryId').select_related('categoryId').filter(
            Q(categoryId=subcategory) | Q(categoryId__parent=subcategory)
        ).aggregate(total=Count('id'))['total'] or 0


class MainCategorySerializer(serializers.ModelSerializer):
    """ Main Category details """
    children = serializers.SerializerMethodField(read_only=True)
    name = serializers.CharField(required=False)
    count = serializers.SerializerMethodField()

    @staticmethod
    def get_children(category):
        children = category.children
        return SubCategorySerializer(children, many=True).data

    class Meta:
        model = ProductCategories
        fields = ['id', 'parent', 'name', 'count', 'is_popular', 'is_hit', 'is_new', 'is_available',
                  'order', 'order_top', 'icon', 'logo', 'children', 'created_at', 'updated_at', 'site']

    @staticmethod
    def get_count(category):
        category_ids = [category.id] + list(category.children.values_list('id', flat=True))
        descendants_query = Q(categoryId__in=category_ids)

        # Use aggregation to count products across all levels
        count = Products.objects.filter(descendants_query).aggregate(total_count=Count('id'))['total_count'] or 0

        return count


class HomeCategorySerializer(serializers.Serializer):
    category_id = serializers.IntegerField(write_only=True)
    product_data = serializers.ListSerializer(child=serializers.CharField(), write_only=True)
    category_data = serializers.ListSerializer(child=serializers.IntegerField(), write_only=True)

    category = serializers.SerializerMethodField(read_only=True)
    children = serializers.SerializerMethodField(read_only=True)
    products = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_category(category):
        return category.name

    @staticmethod
    def get_children(category):
        children = category.children.all().filter(home=True)
        return SubCategorySerializer(children, many=True).data

    @staticmethod
    def get_products(category):
        products = Products.objects.filter(home=True)
        return ProductDetailSerializers(products, many=True).data

    def create(self, validated_data):
        category_id = validated_data.pop('category_id', None)
        product_data = validated_data.pop('product_data', None)
        category_data = validated_data.pop('category_data', None)

        category = get_object_or_404(ProductCategories, id=category_id)

        ProductCategories.objects.filter(home=True).update(home=False)
        Products.objects.filter(home=True).update(home=False)

        category.home = True
        category.save()

        for product_id in product_data:
            product = get_object_or_404(Products, id=product_id)
            product.home = True
            product.save()

        for categoryId in category_data:
            categoryy = get_object_or_404(ProductCategories, id=categoryId)
            categoryy.home = True
            categoryy.save()

        return category


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
    categories = serializers.SerializerMethodField(read_only=True)

    # categoryId = serializers.IntegerField(required=False)

    class Meta:
        model = Products  # Make sure to specify your model here
        fields = '__all__'

    def get_categories(self, product):
        categories = []
        category = product.categoryId
        if category:
            categories.append({'id': category.id, 'name': category.name})
            while category.parent:
                category = category.parent
                categories.append({'id': category.id, 'name': category.name})

        return categories[::-1]

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
        
        code = validated_data.pop('code', instance.code)
        price = validated_data.pop('price', instance.price)
        discount_price = validated_data.pop('discount_price', instance.discount_price)
        instance.code = code if code and code > 0 else instance.code
        instance.price = price if price and price > 0 else instance.price
        instance.discount_price = discount_price if discount_price else instance.discount_price
        categoryId = validated_data.pop('categoryId', instance.categoryId)
        categoryId = categoryId or instance.categoryId
        print(categoryId, instance.categoryId)
        instance.categoryId = categoryId
        category = instance.categoryId
        while category and category.parent:
            category = category.parent
        print(category)
        if validated_data.get('is_new'):
            category.is_new = True
            category.save()
        if validated_data.get('is_hit'):
            category.is_hit = True
            category.save()
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
            'is_popular', 'is_hit', 'is_new', 'created_at', 'images', 'category_name', 'images_set', 'warehouse', 'site', 'sizes'
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
                new_category = ProductCategories.objects.create(name=name, parent=parent_category,
                                                                site=validated_data.get('site', None))
                ExternalCategory.objects.create(external_id=external_id, category=new_category)
            else:
                ExternalCategory.objects.create(external_id=external_id, category=parent_category)

        return category or new_category or parent_category


class CategoryMoveSerializer(serializers.Serializer):
    category_id = serializers.IntegerField(write_only=True)
    categories_data = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    data = serializers.SerializerMethodField(read_only=True)

    def create(self, validated_data):
        category_id = validated_data.pop('category_id', None)
        categories_data = validated_data.pop('categories_data', [])

        # Get the main category
        category = get_object_or_404(ProductCategories, id=category_id)

        # Iterate over the categories_data
        for cat_id in categories_data:
            # Get the current category
            cat = get_object_or_404(ProductCategories, id=cat_id)

            # Move all products to the main category
            cat.products.update(categoryId=category)

            # Move all subcategories and their products to the main category
            for sub in cat.children.all():
                new_sub = ProductCategories.objects.create(name=sub.name, parent=category)
                sub.products.update(categoryId=new_sub)

        return category

    def get_data(self, category):
        return MainCategorySerializer(category).data


class ProductAutoUploaderSerializer(serializers.ModelSerializer):
    color_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    image_set = serializers.JSONField(required=False)
    categoryId = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    sets = serializers.ListSerializer(child=serializers.IntegerField(), required=False)

    class Meta:
        model = Products
        fields = [
            'id', 'name', 'code', 'article', 'product_size', 'material', 'description', 'brand', 'price',
            'price_type', 'discount_price', 'weight', 'barcode', 'ondemand', 'moq', 'days', 'pack', 'prints',
            'created_at', 'updated_at', 'color_name', 'image_set', 'categoryId', 'warehouse', 'site', 'sets', 'sizes'
        ]

    @staticmethod
    def check_color_exists(color_name):
        if color_name:
            color, _ = Colors.objects.get_or_create(name=color_name)
            return color
        return None

    @staticmethod
    def create_img_into_product(img_set, color_instance, product_instance):
        count = 0
        for img in img_set:
            is_gifts = 'api2.gifts.ru' in img['name']
            if not is_gifts:
                ProductImage.objects.create(
                    productID=product_instance,
                    colorID=color_instance,
                    image_url=img['name']
                )
            else:
                count += 1
                image_url = img['name']
                response = get_data(image_url)
                if response and isinstance(response, requests.Response):
                    name = f'{uuid.uuid4()}.jpg'
                    file_path = os.path.join('media', name)
                    with open(file_path, 'wb') as file:
                        file.write(response.content)
                    ProductImage.objects.create(
                        productID=product_instance,
                        colorID=color_instance,
                        image=name
                    )
                else:
                    print(f"Failed to download image from {image_url}")
            if count % 10 == 0:
                time.sleep(5)
        time.sleep(2)

    @staticmethod
    def get_category_instance(cate_id):
        if cate_id is not None:
            external_category = ExternalCategory.objects.filter(external_id=cate_id).first()
            if external_category and external_category.category:
                return external_category.category
        return None

    @staticmethod
    def create_sets(product, sets):
        parent_category = product.categoryId.parent.name
        category = product.categoryId.name
        create_parent_set_category = GiftsBasketCategory.objects.get_or_create(name=parent_category)
        GiftsBasketCategory.objects.get_or_create(name=category,
                                                  parent=create_parent_set_category)
        GiftsBaskets.objects.get_or_create(
            title=product.name,
            small_header=product.name,
            description=product.description

        )
        # for item in sets:
        #     check_product = Products.objects.filter(id=item['product_id'])

        return

    @transaction.atomic
    def create(self, validated_data):
        color_name = validated_data.pop('color_name', None)
        image_set = validated_data.pop('image_set', [])
        category_id = validated_data.pop('categoryId', None)
        # sets = validated_data.pop('sets', [])

        color_instance = self.check_color_exists(color_name)
        category_instance = self.get_category_instance(category_id)

        # Since you are only creating a single product instance, unpacking is appropriate
        product_instance, created = Products.objects.get_or_create(**validated_data)

        if category_instance:
            product_instance.categoryId = category_instance
            product_instance.save()

        # create_set = self.create_sets(product_instance, sets)

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
            'created_at', 'updated_at', 'categoryId', 'warehouse', 'site', 'sizes', 'quantity'
        ]

    def update(self, instance, validated_data):
        # Update the instance fields with new values from validated_data or use existing if not provided
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.price = validated_data.get('price', instance.price)
        instance.discount_price = validated_data.get('discount_price', instance.discount_price)

        # Save the updated instance
        instance.save()

        return instance


class ProductFilterProductSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ProductFilterProducts
        fields = ['id', 'product', 'product_id']

    def update(self, instance, validated_data):
        product = get_object_or_404(Products, id=validated_data.pop('product_id'))
        instance.product = product
        instance.save()
        return instance

    def get_product(self, obj):
        data = ProductDetailSerializers(obj.product, context=self.context)
        return data.data


class FilterProductSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    product_data = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )

    class Meta:
        model = ProductFilterModel
        fields = ['id', 'title', 'products', 'product_data']

    def create(self, validated_data):
        product_data = validated_data.pop('product_data', [])
        product_filter = ProductFilterModel.objects.create(**validated_data)
        for item in product_data:
            product_instance = get_object_or_404(Products, id=item)
            ProductFilterProducts.objects.create(
                filter=product_filter,
                product=product_instance
            )
        return product_filter

    def update(self, instance, validated_data):
        product_data = validated_data.pop('product_data', [])
        for item in product_data:
            product_instance = get_object_or_404(Products, id=item)
            ProductFilterProducts.objects.get_or_create(
                filter=instance,
                product=product_instance
            )
        return super().update(instance, validated_data)

    def get_products(self, obj):
        data = ProductFilterProductSerializer(obj.products.all(), many=True, context=self.context)
        return data.data



