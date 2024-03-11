from django.contrib import admin
from django.utils.safestring import mark_safe

from apps.product.filters import SubCategoryListFilter, MainCategoryListFilter
from apps.product.forms import ProductAdminForm
from apps.product.models import (
    ProductCategories,
    Products
)
from apps.product.proxy import SubCategory, TertiaryCategory


@admin.register(ProductCategories)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(parent__isnull=True)

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ("parent",)
        form = super(ProductCategoryAdmin, self).get_form(request, obj, **kwargs)
        return form


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'parent']
    search_fields = ['name']
    list_filter = [MainCategoryListFilter,]

    def get_queryset(self, request):
        return super().get_queryset(request).filter(parent__isnull=False, parent__parent__isnull=True)

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ("is_popular", 'is_hit', 'is_new')
        form = super(SubCategoryAdmin, self).get_form(request, obj, **kwargs)
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            kwargs["queryset"] = ProductCategories.objects.filter(parent__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(TertiaryCategory)
class TertiaryCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'parent']
    search_fields = ['name']
    list_filter = [SubCategoryListFilter]

    def get_queryset(self, request):
        return super().get_queryset(request).filter(parent__parent__isnull=False)

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ("is_popular", 'is_hit', 'is_new')
        form = super(TertiaryCategoryAdmin, self).get_form(request, obj, **kwargs)
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            kwargs["queryset"] = ProductCategories.objects.filter(parent__isnull=False, parent__parent__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ProductsAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ['id', 'name', 'price', 'price_type']
    search_fields = ['name']

    def product_image(self, obj):
        if obj and obj.productID and obj.productID.image:
            return mark_safe(f'<img src="{obj.productID.image.url}" width="100"/>')
        return "No image"

    product_image.short_description = 'Product Image'


# admin.site.register(ProductCategories, ProductCategoryAdmin)
admin.site.register(Products, ProductsAdmin)
