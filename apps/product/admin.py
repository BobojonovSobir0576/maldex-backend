from django.contrib import admin
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportModelAdmin
from apps.product.filters import CategoryLevelFilter
from apps.product.models import (
    ProductCategories,
    Products,
    Colors,
    ProductImage, ExternalCategory
)


admin.site.site_header = "Maldex Administration"
admin.site.site_title = "Maldex Admin Portal"
admin.site.index_title = "Welcome to Maldex Admin Portal"


@admin.register(ProductCategories)
class ProductCategoryAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'name', 'parent', 'get_externals']
    search_fields = ['name']
    list_filter = [CategoryLevelFilter]

    def get_externals(self, obj):
        externals = obj.external_categories.all()
        IDs = []

        for ex in externals:
            IDs.append(ex.external_id)

        return ', '.join(IDs)

    get_externals.short_description = 'external ID s'


class ExternalCategoriesAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_filter = ['external_id', 'category']


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
    search_fields = ['id', 'name', 'categoryId__name']
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
admin.site.register(ExternalCategory, ExternalCategoriesAdmin)
