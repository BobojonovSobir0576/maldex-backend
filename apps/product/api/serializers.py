import os
import time

import requests
from django.db import transaction
from django.db.models import Q, Count
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from concurrent.futures import ThreadPoolExecutor, as_completed

from apps.gifts_baskets.models import GiftsBasketCategory, GiftsBaskets
from apps.product.api.access import get_data
from apps.product.models import *
from apps.product.proxy import *


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Colors
        fields = ['name', 'hex']


class ProductImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImage
        fields = '__all__'

    def create(self, validated_data):
        if not ('image' not in validated_data or validated_data['image']):
            raise ValidationError({"image": "not found"})
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
        children = category.children.all()
        for category3 in children:
            category_ids += list(category3.children.values_list('id', flat=True))

        # Use aggregation to count products across all levels
        count = Products.objects.filter(categoryId__in=category_ids).aggregate(
            total_count=Count('id'))['total_count'] or 0
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

    @staticmethod
    def get_products(category):
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


class ProductDetailSerializers(serializers.ModelSerializer):
    """ Product details """
    images_set = serializers.SerializerMethodField(read_only=True)
    images = serializers.ListField(write_only=True, required=False)
    deleted_images = serializers.ListField(write_only=True, required=False)
    article = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    categories = serializers.SerializerMethodField(read_only=True)
    colorID = ColorSerializer(read_only=True)
    color = serializers.CharField(write_only=True)
    colors = serializers.SerializerMethodField(read_only=True)
    items = serializers.ListField(write_only=True)
    discounts = serializers.JSONField(read_only=True)

    class Meta:
        model = Products
        fields = '__all__'

    def get_colors(self, product):
        color_name = product.colorID.name.lower()
        product_name = product.name
        without_color_name = product_name[:product_name.index(color_name)] if color_name in product_name else product_name
        space_index = without_color_name[::-1].find(' ')
        common_name = without_color_name[:- space_index - 1]
        similar_products = Products.objects.filter(name__icontains=common_name)
        colors = [{
                      'color': product.colorID.name,
                      'hex': product.colorID.hex,
                      'product': ColorProductSerializers(product, context=self.context).data
                  } if product.colorID else
                  {'color': None, 'product': ColorProductSerializers(product).data, 'hex': '#ffffff'} for product in similar_products]
        return colors

    @staticmethod
    def get_categories(product):
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
        items = validated_data.pop('items', [])
        discounts = []
        for item in items:
            discounts.append({'name': item.get('[name]'), 'count': item.get('[count]')})
        color = validated_data.pop('color', None)
        color = color.lower() if color else color
        color_instance, created = Colors.objects.get_or_create(name=color)
        validated_data['discounts'] = discounts
        product_instance = Products.objects.create(**validated_data, colorID=color_instance)
        for image_data in images:
            image_data['productID'] = product_instance.id
            image_data['colorID'] = {
                'name': image_data['color'].lower()
            }
            image_serializer = ProductImageSerializer(data=image_data, context={'request': self.context['request']})
            if image_serializer.is_valid():
                image_serializer.save()
            else:
                raise ValueError(image_serializer.errors)

        return product_instance

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', [])
        items = validated_data.pop('items', instance.discounts)
        discounts = []
        for item in items:
            discounts.append({'name': item.get('[name]'), 'count': item.get('[count]')})
        color = validated_data.pop('color', instance.colorID.name)
        color = color.lower() if color else color
        color_instance, created = Colors.objects.get_or_create(name=color)
        validated_data['discounts'] = discounts
        validated_data['colorID'] = color_instance
        for image_data in images_data:
            if image_data['image']:
                image_data['productID'] = instance.id
                image_data['colorID'] = {
                    'name': image_data['color'].lower()
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
        instance.categoryId = categoryId
        category = instance.categoryId
        while category and category.parent:
            category = category.parent
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
        } for image in images]


class ProductListSerializers(ProductDetailSerializers):

    class Meta:
        model = Products
        fields = ['id', 'name', 'images_set', 'article', 'colorID', 'brand', 'price', 'price_type', 'discount_price',
                  'is_popular', 'is_hit', 'is_new', 'site', 'categoryId', 'colors',  'warehouse']
        
        
class ColorProductSerializers(ProductDetailSerializers):

    class Meta:
        model = Products
        fields = ['id', 'name', 'images_set', 'article', 'colorID',  'warehouse']


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

    @staticmethod
    def get_data(category):
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
        return Colors.objects.get_or_create(name=color_name)[0] if color_name else None

    @staticmethod
    def fetch_and_save_image(img, product_instance):
        is_gifts = 'api2.gifts.ru' in img['name']
        if is_gifts:
            image_url = img['name']
            response = get_data(image_url)
            if response and isinstance(response, requests.Response):
                name = f'{uuid.uuid4()}.jpg'
                file_path = os.path.join('media', name)
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                return ProductImage(productID=product_instance, image=name)
            else:
                print(f"Failed to download image from {image_url}")
                return None
        else:
            return ProductImage(productID=product_instance, image_url=img['name'])

    @staticmethod
    def create_img_into_product(img_set, product_instance):
        start = time.time()
        images_to_create = []

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(ProductAutoUploaderSerializer.fetch_and_save_image, img, product_instance, ) for img in img_set]
            for future in as_completed(futures):
                image = future.result()
                if image:
                    images_to_create.append(image)

        ProductImage.objects.bulk_create(images_to_create)

        first = time.time() - start
        print(f"6 {int(first) // 60}:{int(first % 60)}")

    @staticmethod
    def get_category_instance(cate_id):
        external_category = ExternalCategory.objects.filter(external_id=cate_id).first()
        return external_category.category if external_category and external_category.category else None

    @staticmethod
    def create_sets(product, sets):
        parent_category = product.categoryId.parent.name
        category = product.categoryId.name
        parent_set_category, _ = GiftsBasketCategory.objects.get_or_create(name=parent_category)
        GiftsBasketCategory.objects.get_or_create(name=category, parent=parent_set_category)
        GiftsBaskets.objects.get_or_create(
            title=product.name,
            small_header=product.name,
            description=product.description
        )
        return

    @transaction.atomic
    def create(self, validated_data):
        color_name = validated_data.pop('color_name', None)
        image_set = validated_data.pop('image_set', [])
        category_id = validated_data.pop('categoryId', None)

        color_instance = self.check_color_exists(color_name)
        category_instance = self.get_category_instance(category_id)

        product_instance, created = Products.objects.get_or_create(**validated_data, colorID=color_instance)

        if category_instance:
            product_instance.categoryId = category_instance
            product_instance.save()

        if image_set:
            self.create_img_into_product(image_set, product_instance)

        return product_instance


class ProductAutoUploaderDetailSerializer(serializers.ModelSerializer):
    price = serializers.FloatField()
    discount_price = serializers.FloatField()

    class Meta:
        model = Products
        fields = [
            'id', 'name', 'code', 'article', 'product_size', 'material', 'description', 'brand', 'price',
            'price_type', 'discount_price', 'weight', 'barcode', 'ondemand', 'moq', 'days', 'pack', 'prints',
            'created_at', 'updated_at', 'categoryId', 'warehouse', 'site', 'sizes'
        ]

    @staticmethod
    def check_color_exists(color_name):
        return Colors.objects.get_or_create(name=color_name)[0] if color_name else None

    @staticmethod
    def fetch_and_save_image(img, product_instance):
        is_gifts = 'api2.gifts.ru' in img['name']
        if is_gifts:
            image_url = img['name']
            response = get_data(image_url)
            if response and isinstance(response, requests.Response):
                name = f'{uuid.uuid4()}.jpg'
                file_path = os.path.join('media', name)
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                return ProductImage(productID=product_instance, image=name)
            else:
                print(f"Failed to download image from {image_url}")
                return None
        else:
            return ProductImage(productID=product_instance, image_url=img['name'])

    @staticmethod
    def create_img_into_product(img_set, color_instance, product_instance):
        start = time.time()
        images_to_create = []

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(ProductAutoUploaderSerializer.fetch_and_save_image, img, product_instance,
                                       ) for img in img_set]
            for future in as_completed(futures):
                image = future.result()
                if image:
                    images_to_create.append(image)

        ProductImage.objects.bulk_create(images_to_create)

        first = time.time() - start
        print(f"6 {int(first) // 60}:{int(first % 60)}")

    def update(self, instance, validated_data):
        color_name = validated_data.pop('color_name', None)
        image_set = validated_data.pop('image_set', [])
        # Update the instance fields with new values from validated_data or use existing if not provided
        instance.price = validated_data.get('price', instance.price)
        instance.discount_price = validated_data.get('discount_price', instance.discount_price)
        instance.warehouse = validated_data.get('warehouse', instance.warehouse)
        instance.sizes = validated_data.get('sizes', instance.sizes)
        color_instance = self.check_color_exists(color_name)
        if color_instance:
            instance.colorID = color_instance
        if image_set:
            self.create_img_into_product(image_set, instance)
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


class SiteLogoSerializer(serializers.ModelSerializer):

    class Meta:
        model = SiteLogo
        fields = ('site', 'logo')
