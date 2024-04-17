from django.contrib import admin
from apps.gifts_baskets.models import *
from import_export.admin import ImportExportModelAdmin


class GiftsBasketImageAdmin(admin.TabularInline):
    model = GiftsBasketImages
    extra = 1


class GiftsBasketProductAdmin(admin.TabularInline):
    model = GiftsBasketProduct
    extra = 1


class GiftBasketCategoryAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['name', 'id', 'is_available', 'parent']
    list_filter = ['is_available']


class GiftBasketAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['title', 'id']
    inlines = [GiftsBasketImageAdmin, GiftsBasketProductAdmin]


admin.site.register(GiftsBasketCategory, GiftBasketCategoryAdmin)
admin.site.register(GiftsBaskets, GiftBasketAdmin)
admin.site.register(GiftsBasketImages)
admin.site.register(GiftsBasketProduct)
