from rest_framework import serializers
from apps.banner.models import *
from apps.product.api.serializers import ProductDetailSerializers


class BannerProductListSerializer(serializers.ModelSerializer):
    productID = ProductDetailSerializers(read_only=True)

    class Meta:
        model = BannerProduct
        fields = ['id', 'productID']


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
    productCarouselID = ProductDetailSerializers(read_only=True)

    class Meta:
        model = BannerCarouselProduct
        fields = ['id', 'bannerCarouselID', 'productCarouselID', 'bannerCarouselVideo']


class BannerCarouselListSerializer(serializers.ModelSerializer):
    product_set = serializers.SerializerMethodField()

    class Meta:
        model = Banner
        fields = ['id', 'name', 'product_set']

    def get_product_set(self, obj):
        banner_products = BannerCarouselProduct.objects.filter(bannerCarouselID=obj)
        return BannerCarouselProductListSerializer(banner_products, many=True, read_only=True).data
