from django.contrib import admin

from apps.product.forms.forms import ProductAdminForm
from apps.product.models import (
    ProductCategories,
    Products
)


class CategoriesAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


class ProductsAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ['id', 'name', 'price', 'price_type']


admin.site.register(ProductCategories, CategoriesAdmin)
admin.site.register(Products, ProductsAdmin)
