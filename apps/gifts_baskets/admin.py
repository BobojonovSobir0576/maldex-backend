from django.contrib import admin
from apps.gifts_baskets.models import *
from import_export.admin import ImportExportModelAdmin


class GiftsBasketImageInline(admin.TabularInline):
    model = GiftsBasketImages
    extra = 1


class GiftsBasketProductInline(admin.TabularInline):
    model = GiftsBasketProduct
    extra = 1


class GiftBasketCategoryAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'name', 'is_available', 'parent']
    list_filter = ['is_available']


class GiftBasketAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['title', 'id']
    inlines = [GiftsBasketImageInline, GiftsBasketProductInline]
    filter_horizontal = ('tags',)


class SetCatalogAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['title', 'is_available', 'created_at']
    list_filter = ['is_available']


class SetProductsAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['set_category', 'product_sets', 'quantity', 'id', 'created_at']
    list_filter = ['set_category']


class AdminFilesAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'name', 'created_at']


class GiftsBasketImagesAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    pass


class GiftsBasketProductAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    pass


class TagAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('name',)


class TagCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = []


admin.site.register(GiftsBasketCategory, GiftBasketCategoryAdmin)
admin.site.register(GiftsBaskets, GiftBasketAdmin)
admin.site.register(GiftsBasketImages, GiftsBasketImagesAdmin)
admin.site.register(GiftsBasketProduct, GiftsBasketProductAdmin)
admin.site.register(SetCategory, SetCatalogAdmin)
admin.site.register(SetProducts, SetProductsAdmin)
admin.site.register(AdminFiles, AdminFilesAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(TagCategory, TagCategoryAdmin)
