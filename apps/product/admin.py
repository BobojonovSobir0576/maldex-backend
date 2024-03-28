from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportModelAdmin
from apps.product.filters import SubCategoryListFilter, MainCategoryListFilter
from apps.product.models import (
    ProductCategories,
    Products,
    Colors,
    ProductImage
)
from apps.product.proxy import SubCategory, TertiaryCategory
from django.urls import path
from django.http import JsonResponse

admin.site.site_header = "Maldex Administration"
admin.site.site_title = "Maldex Admin Portal"
admin.site.index_title = "Welcome to Maldex Admin Portal"


@admin.register(ProductCategories)
class ProductCategoryAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


class ColorInline(admin.TabularInline):
    model = Colors


class ColorAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    model = Colors
    list_display = ['id', 'name']
    search_fields = ['name']


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    inlines = [ColorInline]


class ProductsAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'price_type', 'category_hierarchy']
    search_fields = ['name', 'categoryId__name']
    autocomplete_fields = ['categoryId']
    inlines = [ProductImageInline]

    def category_hierarchy(self, obj):
        names = []
        category = obj.categoryId
        while category is not None:
            names.append(category.name)
            category = category.parent
        return " > ".join(names)
    category_hierarchy.short_description = 'Category Hierarchy'


    def product_image(self, obj):
        if obj and obj.productID and obj.productID.image:
            return mark_safe(f'<img src="{obj.productID.image.url}" width="100"/>')
        return "No image"

    product_image.short_description = 'Product Image'


admin.site.register(Products, ProductsAdmin)
admin.site.register(Colors, ColorAdmin)
admin.site.register(ProductImage)