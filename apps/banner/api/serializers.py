from rest_framework import serializers
from apps.banner.models import *
from apps.banner.utils import create_banner_products, create_banner_carousel_products
from apps.product.api.serializers import ProductDetailSerializers


class BannerProductListSerializer(serializers.ModelSerializer):
    productID = serializers.SerializerMethodField()

    class Meta:
        model = BannerProduct
        fields = ['id', 'productID']

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def get_productID(self, obj):
        data = ProductDetailSerializers(obj.productID, context=self.context)
        return data.data


class BannerListSerializer(serializers.ModelSerializer):
    product_set = serializers.SerializerMethodField()
    product_data = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )

    class Meta:
        model = Banner
        fields = ['id', 'name', 'product_set', 'product_data', 'order_by_id']

    def create(self, validated_data):
        product_data = validated_data.pop('product_data', [])
        create_banner = Banner.objects.create(**validated_data)
        create_banner_products(product_data, create_banner)
        return create_banner

    def update(self, instance, validated_data):
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

    class Meta:
        model = BannerCarousel
        fields = ['id', 'name', 'product_set', 'product_data']

    def create(self, validated_data):
        product_data = validated_data.pop('product_data', [])
        create_banner_carousel = BannerCarousel.objects.create(**validated_data)
        create_banner_carousel_products(product_data, create_banner_carousel)
        return create_banner_carousel

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def get_product_set(self, obj):
        data = BannerCarouselProductListSerializer(obj.bannerCarouselID.all(), many=True, context=self.context)
        return data.data
