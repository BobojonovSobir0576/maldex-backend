import uuid
from django.utils.translation import gettext_lazy as _
from django.db import models
from apps.product.models import Products


class Banner(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Name of Banner'), max_length=155, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "banner"
        verbose_name = "Banner"
        verbose_name_plural = "Banners"


class BannerProduct(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bannerID = models.ForeignKey(Banner, on_delete=models.CASCADE, null=True, blank=True, related_name='bannerID')
    productID = models.ForeignKey(Products, on_delete=models.CASCADE, null=True, blank=True,
                                  related_name='bannerProduct')
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.bannerID.name


class BannerCarousel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Name of Banner Carousel'), max_length=155, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "banner_carousel"
        verbose_name = "Banner Carousel"
        verbose_name_plural = "Banner Carousel"


class BannerCarouselProduct(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bannerCarouselID = models.ForeignKey(BannerCarousel, on_delete=models.CASCADE, null=True, blank=True, related_name='bannerCarouselID')
    productCarouselID = models.ForeignKey(Products, on_delete=models.CASCADE, null=True, blank=True,
                                  related_name='bannerCarouselProduct')
    bannerCarouselVideo = models.FileField(upload_to="media/banner/carousel/video/", null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.bannerCarouselID.name
