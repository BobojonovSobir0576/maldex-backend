from django.shortcuts import get_object_or_404
from rest_framework import serializers
from apps.banner.models import *
from apps.banner.utils import create_banner_products, create_banner_carousel_products, update_banner_products, \
    create_banner_buttons
from apps.product.api.serializers import ProductDetailSerializers


class BannerProductListSerializer(serializers.ModelSerializer):
    productID = serializers.SerializerMethodField()
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = BannerProduct
        fields = ['id', 'productID', 'product_id']

    def update(self, instance, validated_data):
        product = get_object_or_404(Products, id=validated_data.pop('product_id'))
        instance.productID = product
        instance.save()
        return instance

    def get_productID(self, obj):
        data = ProductDetailSerializers(obj.productID, context=self.context)
        return data.data


class ButtonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Button
        fields = ['title', 'url']


class BannerListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    product_set = serializers.SerializerMethodField()
    product_data = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )

    class Meta:
        model = Banner
        fields = ['id', 'name', 'product_set', 'product_data', 'order_by_id', 'buttons', 'buttons_data']

    def create(self, validated_data):
        product_data = validated_data.pop('product_data', [])
        create_banner = Banner.objects.create(**validated_data)
        create_banner_products(product_data, create_banner)
        return create_banner

    def update(self, instance, validated_data):
        product_data = validated_data.pop('product_data', [])
        update_banner_products(instance, product_data)
        return super().update(instance, validated_data)

    def get_product_set(self, obj):
        data = BannerProductListSerializer(obj.bannerID.all(), many=True, context=self.context)
        return data.data


class BannerCarouselProductListSerializer(serializers.ModelSerializer):
    productCarouselID = serializers.SerializerMethodField()

    class Meta:
        model = BannerCarouselProduct
        fields = ['id', 'bannerCarouselID', 'productCarouselID', 'bannerCarouselVideo']

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def get_productCarouselID(self, obj):
        data = ProductDetailSerializers(obj.productCarouselID, context=self.context)
        return data.data


class BannerCarouselListSerializer(serializers.ModelSerializer):
    product_set = serializers.SerializerMethodField()
    product_data = serializers.ListSerializer(
        child=serializers.IntegerField(required=True),
        write_only=True
    )
    buttons = ButtonSerializer(many=True, read_only=True)
    buttons_data = serializers.ListSerializer(child=ButtonSerializer())

    class Meta:
        model = BannerCarousel
        fields = ['id', 'name', 'product_set', 'product_data', 'buttons', 'buttons_data']

    def create(self, validated_data):
        product_data = validated_data.pop('product_data', [])
        buttons_data = validated_data.pop('buttons_data', [])
        create_banner_carousel = BannerCarousel.objects.create(**validated_data)
        create_banner_carousel_products(product_data, create_banner_carousel)
        create_banner_buttons(buttons_data, create_banner_carousel)
        return create_banner_carousel

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def get_product_set(self, obj):
        data = BannerCarouselProductListSerializer(obj.bannerCarouselID.all(), many=True, context=self.context)
        return data.data
