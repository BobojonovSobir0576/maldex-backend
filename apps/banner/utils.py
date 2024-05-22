from django.shortcuts import get_object_or_404

from apps.banner.models import BannerProduct, Button, BannerCarouselProduct
from apps.product.models import Products


def create_banner_products(product_data, create_banner):
    for item in product_data:
        product_instance = get_object_or_404(Products, id=item)
        create_banner_product = BannerProduct.objects.create(
            bannerID=create_banner,
            productID=product_instance
        )
    return create_banner_product


def create_banner_buttons(buttons_data, banner_carousel):
    for button in buttons_data:
        Button.objects.get_or_create(
            title=button.title,
            url=button.url,
            banner_carousel=banner_carousel
        )
    return None


def update_banner_products(banner, product_data):
    for item in product_data:
        product_instance = get_object_or_404(Products, id=item)
        BannerProduct.objects.get_or_create(
            bannerID=banner,
            productID=product_instance
        )
    return None


def create_banner_carousel_products(product_data, create_banner_carousel):
    for item in product_data:
        product_instance = get_object_or_404(Products, id=item)
        create_banner_carousel_product = BannerCarouselProduct.objects.get_or_create(
            bannerCarouselID=create_banner_carousel,
            productCarouselID=product_instance
        )
    return None
