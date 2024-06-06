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
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        print(self.value())
        if self.value() == 'Yes':
            return queryset.filter(~Q(sizes='') & ~Q(sizes=None))
        elif self.value() == 'No':
            return queryset.filter(Q(sizes='') | Q(sizes=None))
        return queryset

class HasWarehouseFilter(SimpleListFilter):
    title = 'Has Warehouse'
    parameter_name = 'has_warehouse'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(~Q(warehouse='') & ~Q(warehouse=None))
        elif self.value() == 'no':
            return queryset.filter(Q(warehouse='') | Q(warehouse=None))
        return queryset


class HasImageFilter(SimpleListFilter):
    title = 'Has Image'
    parameter_name = 'has_image'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(images_set__image__isnull=False) | queryset.filter(images_set__image_url__isnull=False)
        elif self.value() == 'No':
            return queryset.exclude(images_set__image__isnull=False).exclude(images_set__image_url__isnull=False)
        return queryset

# Admin configuration for Product Categories
@admin.register(ProductCategories)
class CategoryAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['icon_image', 'name', 'id', 'order', 'get_externals', 'site']
    fields = ['name', 'parent', 'is_popular', 'is_hit', 'is_new', 'is_available', 'home', 'icon', 'logo', 'order', 'order_top', 'order_by_site']
    search_fields = ['name']
    readonly_fields = ['icon_image']
    autocomplete_fields = ['parent']

    def get_queryset(self, request):
        qs = super().get_queryset(request).filter(parent=None)
        return qs

    def get_externals(self, obj):
        # Display associated external IDs
        externals = obj.external_categories.all()
        ids = []

        for ex in externals:
            ids.append(ex.external_id)

        return ', '.join(ids)

    def icon_image(self, obj):
        # Display icon image
        if obj and obj.icon:
            return mark_safe(f'<img src="{obj.icon.url}" width="30" height="30"/>')
        return "No image"

    icon_image.short_description = 'Product Image'
    get_externals.short_description = 'External IDs'


# Admin configuration for Subcategories
@admin.register(SubCategory)
class SubCategoryAdmin(CategoryAdmin, ImportExportModelAdmin):
    list_display = ['name', 'id', 'parent', 'get_externals', 'site']
    fields = ['name', 'parent']
    search_fields = ['name']
    list_filter = ['parent']

    def get_queryset(self, request):
        qs = SubCategory.objects.all()
        return qs

    def get_form(self, request, obj=None, **kwargs):
        # Make parent field required
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['parent'].required = True
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Limit parent field queryset to main categories
        if db_field.name == 'parent':
            kwargs['queryset'] = ProductCategories.objects.filter(parent=None)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# Admin configuration for Tertiary Categories
@admin.register(TertiaryCategory)
class TertiaryCategoryAdmin(SubCategoryAdmin, ImportExportModelAdmin):

    def get_queryset(self, request):
        qs = TertiaryCategory.objects.all()
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Limit parent field queryset to subcategories
        if db_field.name == 'parent':
            kwargs['queryset'] = SubCategory.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# Admin configuration for External Categories
class ExternalCategoriesAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_filter = ['external_id', 'category']
    autocomplete_fields = ['category']


# Inline admin configuration for Colors
class ColorInline(admin.TabularInline):
    model = Colors


# Admin configuration for Colors
class ColorAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    model = Colors
    list_display = ['name', 'id']
    search_fields = ['name']


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
class ProductsAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['name', 'id', 'article', 'price', 'site', 'category_hierarchy', 'has_image', 'has_sizes', 'has_warehouse',
                    'colorID']
    search_fields = ['id', 'name', 'categoryId__name']
    autocomplete_fields = ['categoryId']
    fields = [
        'name', 'categoryId', 'code', 'article', 'product_size', 'material', 'description',
        'brand', 'price', 'price_type', 'discount_price', 'weight', 'barcode', 'ondemand',
        'moq', 'days', 'is_popular', 'is_hit', 'is_new', 'pack', 'warehouse', 'site', 'sizes', 'colorID', 'prints'
    ]
    inlines = [ProductImageInline]
    list_filter = ['is_new', 'is_popular', 'is_hit', 'site', HasImageFilter, HasSizesFilter, HasWarehouseFilter]
    list_per_page = 500
    ordering = ('-created_at',)

    def category_hierarchy(self, obj):
        # Display hierarchy of categories
        names = []
        category = obj.categoryId
        while category is not None:
            names.append(category.name)
            category = category.parent
        return " > ".join(names[::-1])

    category_hierarchy.short_description = 'Category Hierarchy'

    def product_image(self, obj):
        # Display product image
        if obj and obj.productID and obj.productID.image:
            return mark_safe(f'<img src="{obj.productID.image.url}" width="100"/>')
        return "No image"

    product_image.short_description = 'Product Image'

    def has_image(self, obj):
        # Check if the product has an image or image URL
        if obj.images_set.exists():
            for image in obj.images_set.all():
                if image.image or image.image_url:
                    return "Yes"
        return "No"

    has_image.short_description = 'Has Image'

    def has_sizes(self, obj):
        if obj.sizes:
            return 'Yes'
        return 'No'

    has_sizes.short_description = 'Has sizes'

    def has_warehouse(self, obj):
        if obj.warehouse:
            return 'Yes'
        return 'No'

    has_warehouse.short_description = 'Has warehouse'

class ProductImageAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    pass


@admin.register(SiteLogo)
class SiteLogoAdmin(admin.ModelAdmin):
    list_display = ['site', 'logo']
    fields = ['site', 'logo']


# Register models with the admin site
admin.site.register(Products, ProductsAdmin)
admin.site.register(Colors, ColorAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
admin.site.register(ExternalCategory, ExternalCategoriesAdmin)
