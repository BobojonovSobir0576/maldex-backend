from django.shortcuts import get_object_or_404

from apps.banner.models import BannerProduct
from apps.product.models import Products


def create_banner_products(product_data, create_banner):
    for item in product_data:
        product_instance = get_object_or_404(Products, id=item)
        create_banner_product = BannerProduct.objects.create(
            bannerID=create_banner,
            productID=product_instance
        )
    return create_banner_product


def create_banner_carousel_products(product_data, create_banner_carousel):
    for item in product_data:
        product_instance = get_object_or_404(Products, id=item)
        create_banner_carousel_product = BannerProduct.objects.create(
            bannerID=create_banner_carousel,
            productID=product_instance
        )
    return create_banner_carousel_product
