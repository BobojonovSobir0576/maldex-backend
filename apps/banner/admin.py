from django.contrib import admin
from apps.banner.models import Banner, BannerProduct, BannerCarousel, BannerCarouselProduct
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin


class BannerProductInline(admin.TabularInline):
    model = BannerProduct
    extra = 1
    autocomplete_fields = ['productID']
    readonly_fields = ['product_image',]

    def product_image(self, obj):
        if obj and obj.productID and obj.productID.image:
            return format_html('<img src="{}" width="50%" height="50%"/>', obj.productID.image.url)
        return "No image"


class BannerAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    inlines = [
        BannerProductInline,
    ]
    list_display = ['id', 'name', 'created_at']
    search_fields = ['name']
    ordering = ['-created_at']
    readonly_fields = ['created_at']

    fieldsets = [
        (None, {'fields': ['name', 'created_at']}),
    ]


class BannerCarouselProductInline(admin.TabularInline):
    model = BannerCarouselProduct
    extra = 1
    autocomplete_fields = ['productCarouselID']
    readonly_fields = ['product_image', 'banner_carousel_video']

    def product_image(self, obj):
        if obj and obj.productCarouselID and obj.productCarouselID.image:
            return format_html('<img src="{}" width="50%" height="50%"/>', obj.productCarouselID.image.url)
        return "No image"

    product_image.short_description = 'Product Image'

    def banner_carousel_video(self, obj):
        if obj and obj.bannerCarouselVideo:
            return format_html(
                '<video width="320" height="240" controls> <source src="{}">Your browser does not support the video tag.</video>',
                obj.bannerCarouselVideo.url
            )
        return "No video"

    banner_carousel_video.short_description = 'Banner Carousel Video'


class BannerCarouselAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    inlines = [
        BannerCarouselProductInline,
    ]
    list_display = ['id', 'name', 'created_at']
    search_fields = ['name']
    ordering = ['-created_at']
    readonly_fields = ['created_at']

    fieldsets = [
        (None, {'fields': ['name', 'created_at']}),
    ]


admin.site.register(Banner, BannerAdmin)
admin.site.register(BannerCarousel, BannerCarouselAdmin)
