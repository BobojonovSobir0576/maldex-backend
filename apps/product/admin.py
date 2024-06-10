from django.contrib import admin
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportModelAdmin
from apps.product.models import (
    ProductCategories,
    Products,
    Colors,
    ProductImage,
    ExternalCategory,
    SiteLogo
)
from apps.product.proxy import SubCategory, TertiaryCategory
from django.contrib.admin import SimpleListFilter
from django.db.models import Q

# Set the admin site titles
admin.site.site_header = "Maldex Administration"
admin.site.site_title = "Maldex Admin Portal"
admin.site.index_title = "Welcome to Maldex Admin Portal"


class HasSizesFilter(SimpleListFilter):
    title = 'Has Sizes'
    parameter_name = 'has_sizes'

    def lookups(self, request, model_admin):
        return ('yes', 'Yes'), ('no', 'No')

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(Q(sizes='') | Q(sizes=None))
        elif self.value() == 'no':
            return queryset.filter(Q(sizes='') | Q(sizes=None))
        return queryset


class HasWarehouseFilter(SimpleListFilter):
    title = 'Has Warehouse'
    parameter_name = 'has_warehouse'

    def lookups(self, request, model_admin):
        return ('yes', 'Yes'), ('no', 'No')

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(Q(warehouse='') | Q(warehouse=None))
        elif self.value() == 'no':
            return queryset.filter(Q(warehouse='') | Q(warehouse=None))
        return queryset


class HasImageFilter(SimpleListFilter):
    title = 'Has Image'
    parameter_name = 'has_image'

    def lookups(self, request, model_admin):
        return ('yes', 'Yes'), ('no', 'No')

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(Q(images_set__image__isnull=False) | Q(images_set__image_url__isnull=False))
        elif self.value() == 'no':
            return queryset.exclude(Q(images_set__image__isnull=False) & Q(images_set__image_url__isnull=False))
        return queryset


# Base Category Admin Configuration
class BaseCategoryAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    search_fields = ['name']
    readonly_fields = ['icon_image']
    autocomplete_fields = ['parent']

    def get_externals(self, obj):
        return ', '.join(external.external_id for external in obj.external_categories.all())

    def icon_image(self, obj):
        if obj.icon:
            return mark_safe(f'<img src="{obj.icon.url}" width="30" height="30"/>')
        return "No image"

    icon_image.short_description = 'Icon'
    get_externals.short_description = 'External IDs'


# Admin configuration for Product Categories
@admin.register(ProductCategories)
class CategoryAdmin(BaseCategoryAdmin):
    list_display = ['icon_image', 'name', 'id', 'order', 'get_externals', 'site']
    fields = [
        'name', 'parent', 'seo_title', 'seo_description', 'is_popular', 'is_hit',
        'is_new', 'is_available', 'home', 'icon', 'logo', 'order_top', 'order_by_site'
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).filter(parent=None)


# Admin configuration for Subcategories
@admin.register(SubCategory)
class SubCategoryAdmin(BaseCategoryAdmin):
    list_display = ['name', 'id', 'parent', 'get_externals', 'site']
    fields = ['name', 'parent', 'seo_title', 'seo_description']
    list_filter = ['parent']

    def get_queryset(self, request):
        return SubCategory.objects.all()

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['parent'].required = True
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'parent':
            kwargs['queryset'] = ProductCategories.objects.filter(parent=None)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(TertiaryCategory)
class TertiaryCategoryAdmin(SubCategoryAdmin):

    def get_queryset(self, request):
        return TertiaryCategory.objects.all()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'parent':
            kwargs['queryset'] = SubCategory.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# Admin configuration for External Categories
@admin.register(ExternalCategory)
class ExternalCategoriesAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_filter = ['external_id', 'category']
    autocomplete_fields = ['category']


# Inline admin configuration for Colors
class ColorInline(admin.TabularInline):
    model = Colors


# Admin configuration for Colors
@admin.register(Colors)
class ColorAdmin(ImportExportModelAdmin):
    list_display = ['display_color', 'hex']
    search_fields = ['name']
    readonly_fields = ['display_color']

    def display_color(self, obj):
        return mark_safe(f'<span style="color: {obj.hex}; font-weight: bold;'
                         f'-webkit-text-stroke-width: 0.5px; -webkit-text-stroke-color: black;">{obj.name}</span>')

    display_color.short_description = 'Color'


# Inline admin configuration for Product Images
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    inlines = [ColorInline]
    fields = ('_image', 'image', 'image_url')
    readonly_fields = ('_image',)

    def _image(self, obj):
        image_url = obj.image_url
        html = mark_safe(f'<img src="{image_url}" width=70 height=70 style="object-fit: cover">')
        return html if image_url else ''

    _image.short_description = ''


# Admin configuration for Products
@admin.register(Products)
class ProductsAdmin(ImportExportModelAdmin):
    list_display = [
        'name', 'id', 'article', 'price', 'site', 'category_hierarchy',
        'has_image', 'has_sizes', 'has_warehouse', 'colorID'
    ]
    search_fields = ['id', 'name', 'categoryId__name']
    autocomplete_fields = ['categoryId']
    fields = [
        'name', 'categoryId', 'code', 'article', 'product_size', 'material',
        'description', 'brand', 'price', 'price_type', 'discount_price',
        'weight', 'barcode', 'ondemand', 'moq', 'days', 'is_popular',
        'is_hit', 'is_new', 'pack', 'warehouse', 'site', 'sizes', 'colorID', 'prints'
    ]
    inlines = [ProductImageInline]
    list_filter = [
        'is_new', 'is_popular', 'is_hit', 'site', HasImageFilter,
        HasSizesFilter, HasWarehouseFilter
    ]
    list_per_page = 500
    ordering = ('-created_at',)

    def category_hierarchy(self, obj):
        categories = []
        category = obj.categoryId
        while category:
            categories.append(category.name)
            category = category.parent
        return " > ".join(reversed(categories))

    category_hierarchy.short_description = 'Category Hierarchy'

    def has_image(self, obj):
        return "Yes" if obj.images_set.filter(Q(image__isnull=False) | Q(image_url__isnull=False)).exists() else "No"

    has_image.short_description = 'Has Image'

    def has_sizes(self, obj):
        return 'Yes' if obj.sizes else 'No'

    has_sizes.short_description = 'Has Sizes'

    def has_warehouse(self, obj):
        return 'Yes' if obj.warehouse else 'No'

    has_warehouse.short_description = 'Has Warehouse'


@admin.register(ProductImage)
class ProductImageAdmin(ImportExportModelAdmin):
    pass


@admin.register(SiteLogo)
class SiteLogoAdmin(admin.ModelAdmin):
    list_display = ['site', 'logo']
    fields = ['site', 'logo']
