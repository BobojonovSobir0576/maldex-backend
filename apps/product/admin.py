from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportModelAdmin
from apps.product.filters import SubCategoryListFilter, MainCategoryListFilter
from apps.product.forms import ProductAdminForm
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

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(parent__isnull=True)

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ("parent",)
        form = super(ProductCategoryAdmin, self).get_form(request, obj, **kwargs)
        return form


@admin.register(SubCategory)
class SubCategoryAdmin(ImportExportModelAdmin, admin.ModelAdmin):
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
class TertiaryCategoryAdmin(ImportExportModelAdmin, admin.ModelAdmin):
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
    form = ProductAdminForm
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