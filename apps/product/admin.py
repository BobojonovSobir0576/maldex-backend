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
from apps.product.proxy import SubCategory, TertiaryCategory


admin.site.site_header = "Maldex Administration"
admin.site.site_title = "Maldex Admin Portal"
admin.site.index_title = "Welcome to Maldex Admin Portal"


@admin.register(ProductCategories)
class CategoryAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['name', 'id', 'get_externals']
    fields = ['name', 'is_popular', 'is_hit', 'is_new', 'is_available', 'icon', 'logo']
    search_fields = ['name']
    list_filter = [CategoryLevelFilter]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['icon'].required = True
        form.base_fields['logo'].required = True
        return form

    def get_externals(self, obj):
        externals = obj.external_categories.all()
        IDs = []

        for ex in externals:
            IDs.append(ex.external_id)

        return ', '.join(IDs)

    get_externals.short_description = 'external ID s'

@admin.register(SubCategory)
class SubCategoryAdmin(CategoryAdmin, ImportExportModelAdmin):
    list_display = ['name', 'id', 'parent', 'get_externals']
    fields = ['name', 'parent']
    search_fields = ['name']
    list_filter = ['parent']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['parent'].required = True  # Make parent field required
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'parent':
            kwargs['queryset'] = ProductCategories.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(TertiaryCategory)
class TertiaryCategoryAdmin(CategoryAdmin, ImportExportModelAdmin):
    list_display = ['name', 'id', 'parent', 'get_externals']
    fields = ['name', 'parent']
    search_fields = ['name']
    list_filter = ['parent']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['parent'].required = True  # Make parent field required
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'parent':
            kwargs['queryset'] = SubCategory.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ExternalCategoriesAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_filter = ['external_id', 'category']


class ColorInline(admin.TabularInline):
    model = Colors


class ColorAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    model = Colors
    list_display = ['name', 'id']
    search_fields = ['name']


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    inlines = [ColorInline]


class ProductsAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'price_type', 'category_hierarchy']
    search_fields = ['id', 'name', 'categoryId__name']
    autocomplete_fields = ['categoryId']
    fields = [
        'name', 'categoryId', 'code', 'article', 'product_size', 'material', 'description',
        'brand', 'price', 'price_type', 'discount_price', 'weight', 'barcode', 'ondemand',
        'moq', 'days', 'is_popular', 'is_hit', 'is_new', 'pack', 
    ]
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
