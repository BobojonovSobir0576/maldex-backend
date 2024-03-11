from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework import serializers
from apps.banner.models import *
from apps.product.api.serializers import ProductDetailSerializers


class BannerProductListSerializer(serializers.ModelSerializer):
    bannerID = serializers.SerializerMethodField()
    productID = ProductDetailSerializers(read_only=True)

    class Meta:
        model = BannerProduct
        fields = ['id', 'bannerID', 'productID']

    def get_bannerID(self, obj):
        if obj.bannerID:
            return {"id": obj.bannerID.id, "name": obj.bannerID.name}
        return None


class BannerListSerializer(serializers.ModelSerializer):
    product_set = serializers.SerializerMethodField()

    class Meta:
        model = Banner
        fields = ['id', 'name', 'product_set']

    def get_product_set(self, obj):
        banner_products = BannerProduct.objects.filter(
            bannerID=obj)
        return BannerProductListSerializer(banner_products, many=True, read_only=True).data


class BannerCarouselProductListSerializer(serializers.ModelSerializer):
    bannerCarouselID = serializers.SerializerMethodField()
    productCarouselID = ProductDetailSerializers(read_only=True)

    class Meta:
        model = BannerCarouselProduct
        fields = ['id', 'bannerCarouselID', 'productCarouselID', 'bannerCarouselVideo']

    def get_bannerCarouselID(self, obj):
        if obj.bannerCarouselID:
            return {"id": obj.bannerCarouselID.id, "name": obj.bannerCarouselID.name}
        return None


class BannerCarouselListSerializer(serializers.ModelSerializer):
    product_set = serializers.SerializerMethodField()

    class Meta:
        model = Banner
        fields = ['id', 'name', 'product_set']

    def get_product_set(self, obj):
        banner_products = BannerCarouselProduct.objects.filter(
            bannerCarouselID=obj)
        return BannerCarouselProductListSerializer(banner_products, many=True, read_only=True).data
