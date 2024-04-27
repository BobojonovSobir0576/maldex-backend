from django.db import transaction
from rest_framework import serializers
from apps.gifts_baskets.models import *
from apps.gifts_baskets.utils import create_set_products
from apps.product.api.serializers import ProductDetailSerializers


class CategoryTagListSerializer(serializers.ModelSerializer):
    tag_set = serializers.SerializerMethodField()

    class Meta:
        model = TagCategory
        fields = ['id', 'name', 'tag_set']

    def get_tag_set(self, obj):
        data = TagSerializer(obj.categoryTag.all(), many=True)
        return data.data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'order', 'tag_category')


class GiftBasketCategoryListSerializer(serializers.ModelSerializer):

    class Meta:
        model = GiftsBasketCategory
        fields = ['id', 'name', 'is_available', 'parent']

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class GiftBasketCategoryDetailSerializers(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    product_set = serializers.SerializerMethodField()

    class Meta:
        model = GiftsBasketCategory
        fields = ['id', 'name', 'is_available', 'children', 'product_set']

    def get_children(self, obj):
        children_serializer = GiftBasketCategoryDetailSerializers(obj.children.all(), many=True, context=self.context)
        return children_serializer.data

    def get_product_set(self, obj):
        data = GiftBasketDetailSerializers(obj.cateGiftBasket.all(), many=True, context=self.context)
        return data.data


class GiftsBasketProductSerializers(serializers.ModelSerializer):
    product_sets = ProductDetailSerializers(read_only=True)

    class Meta:
        model = GiftsBasketProduct
        fields = ['id', 'product_sets', 'quantity']


class GiftsBasketProductDetailsSerializers(serializers.ModelSerializer):

    class Meta:
        model = GiftsBasketProduct
        fields = ['id', 'product_sets', 'quantity']

    def update(self, instance, validated_data):
        instance.quantity -= int(validated_data['quantity'])
        (instance.quantity > 0 and [instance.save()] or [instance.delete()])[0]
        return instance


class GiftsBasketImagesSerializers(serializers.ModelSerializer):
    class Meta:
        model = GiftsBasketImages
        fields = ['id', 'images']

    def update(self, instance, validated_data):
        new_image = self.context.get('image')
        instance.images = new_image or instance.images
        instance.save()
        return instance


class GiftBasketListSerializers(serializers.ModelSerializer):
    gift_basket_category = GiftBasketCategoryDetailSerializers(many=True, read_only=True)
    category_data = serializers.JSONField(write_only=True, required=False)
    basket_images = GiftsBasketImagesSerializers(many=True, read_only=True)
    images_data = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False), write_only=True, required=False)
    basket_products = GiftsBasketProductSerializers(many=True, read_only=True)
    products_data = serializers.JSONField(write_only=True, required=False)
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = GiftsBaskets
        fields = ['id', 'title', 'description', 'gift_basket_category', 'category_data',  'basket_images',
                  'images_data', 'basket_products', 'products_data', 'other_sets',
                  'article', 'price', 'price_type', 'discount_price', 'small_header', 'created_at', 'tags']

    def create(self, validated_data):
        categories = validated_data.pop('category_data', [])
        images = validated_data.pop('images_data', [])
        products = validated_data.pop('products_data', [])
        tags = validated_data.pop('tags', [])
        basket = GiftsBaskets.objects.create(**validated_data)
        basket.gift_basket_category.set(categories)

        for image_data in images:
            GiftsBasketImages.objects.create(gift_basket=basket, images=image_data)
        price_set = 0
        for product_info in products:
            product = Products.objects.get(id=product_info['product_sets'])
            price_set = product.price
            price_set += product.price
            GiftsBasketProduct.objects.create(
                gift_basket=basket, product_sets=product, quantity=product_info['quantity'])

        for tag in tags:
            tag_name = tag['name']
            tag_instance = Tag.objects.get_or_create(name=tag_name)
            basket.tags.add(tag_instance[0])

        basket.price = price_set
        basket.save()
        return basket

    def update(self, instance, validated_data):
        with transaction.atomic():
            instance.title = validated_data.get('title', instance.title)
            instance.description = validated_data.get('description', instance.description)
            instance.save()

            self.update_related_items(
                instance,
                validated_data.pop('basket_images', []),
                GiftsBasketImages,
                'images'
            )

            self.update_related_items(
                instance,
                validated_data.pop('basket_products', []),
                GiftsBasketProduct,
                'product_sets_id',
                extra_fields=['quantity']
            )

        return instance

    def update_related_items(self, instance, related_data, model, key_field, extra_fields=None):
        model_objects = {item.id: item for item in model.objects.filter(gift_basket=instance)}
        updated_items = []
        new_items = []

        for data in related_data:
            item_id = data.get('id')
            if item_id and item_id in model_objects:
                item = model_objects[item_id]
                setattr(item, key_field, data.get(key_field, getattr(item, key_field)))
                if extra_fields:
                    for field in extra_fields:
                        setattr(item, field, data.get(field, getattr(item, field)))
                updated_items.append(item)
            else:
                new_items.append(model(gift_basket=instance, **data))

        model.objects.bulk_update(updated_items, [key_field] + (extra_fields or []))
        model.objects.bulk_create(new_items)


class GiftBasketDetailSerializers(serializers.ModelSerializer):
    gift_basket_images = serializers.SerializerMethodField()
    gift_basket_product = serializers.SerializerMethodField()
    gift_basket_category = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)

    class Meta:
        model = GiftsBaskets
        fields = ['title', 'id', 'description', 'gift_basket_category', 'gift_basket_product', 'gift_basket_images',
                  'other_sets', 'article', 'price', 'price_type', 'discount_price', 'small_header', 'created_at', 'tags']

    def get_gift_basket_images(self, obj):
        children_serializer = GiftsBasketImagesSerializers(obj.basket_images.all(), many=True, context=self.context)
        return children_serializer.data

    def get_gift_basket_product(self, obj):
        data = obj.basket_products.all()
        children_serializer = GiftsBasketProductSerializers(data, many=True, context=self.context)
        return children_serializer.data

    def get_gift_basket_category(self, obj):
        children_serializer = GiftBasketCategoryListSerializer(obj.gift_basket_category.all(), many=True,
                                                               context=self.context.get('request'))
        return children_serializer.data


class SetProductListSerializer(serializers.ModelSerializer):
    product_sets = ProductDetailSerializers(read_only=True)

    class Meta:
        model = SetProducts
        fields = ['id', 'set_category', 'product_sets', 'quantity', 'created_at']

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class SetCategoryListSerializer(serializers.ModelSerializer):
    product_sets = serializers.SerializerMethodField()
    product_data = serializers.JSONField(write_only=True, required=False)

    class Meta:
        model = SetCategory
        fields = ['id', 'title', 'is_available', 'product_sets', 'product_data', 'created_at']

    def create(self, validated_data):
        product_data = validated_data.pop('product_data', [])
        create_set_catalog = SetCategory.objects.create(**validated_data)
        create_set_products(product_data, create_set_catalog)

        return create_set_catalog

    def get_product_sets(self, obj):
        data = SetProductListSerializer(obj.setProducts.all(), many=True, context=self.context)
        return data.data

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class AdminFilesListSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=False)

    class Meta:
        model = AdminFiles
        fields = ['id', 'name', 'file', 'created_at']

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        file = self.context.get('request').FILES.get('file', None)
        instance.file = file or instance.file
        instance.save()
        return super().update(instance, validated_data)
