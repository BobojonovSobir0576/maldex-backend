from django.shortcuts import get_object_or_404

from apps.gifts_baskets.models import SetProducts
from apps.product.models import Products


def create_set_products(obj, set_catalog):
    for item in obj:
        product_instance = get_object_or_404(Products, id=item['product_sets'])
        print(product_instance)

        create_set_product = SetProducts.objects.create(
            set_category=set_catalog,
            product_sets=product_instance,
            quantity=item['quantity']
        )
    return create_set_product
