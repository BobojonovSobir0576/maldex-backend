import uuid
from django.utils.translation import gettext_lazy as _
from django.db import models
from apps.product.models import Products


class Banner(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='Уникальный идентификатор')
    name = models.CharField(_('Название баннера'), max_length=155)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    order_by_id = models.IntegerField(default=0, null=True, blank=True, verbose_name="")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "banner"
        verbose_name = "Баннер"
        verbose_name_plural = "Баннер"


class BannerProduct(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='Уникальный идентификатор')
    bannerID = models.ForeignKey(Banner, on_delete=models.CASCADE, null=True, blank=True, related_name='bannerID',
                                 verbose_name='Идентификатор баннера')
    productID = models.ForeignKey(Products, on_delete=models.CASCADE, null=True, blank=True,
                                  related_name='bannerProduct', verbose_name='Идентификатор товара')
    created_at = models.DateField(auto_now_add=True, verbose_name='Дата публикации')

    def __str__(self):
        return self.bannerID.name

    class Meta:
        db_table = "banner_product"
        verbose_name = "Продукт Баннера"
        verbose_name_plural = "Продукт Баннера"


class BannerCarousel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='Уникальный идентификатор')
    name = models.CharField(_('Название баннерной карусели'), max_length=155, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')

    def __str__(self):
        return self.name

    class Meta:
        db_table = "banner_carousel"
        verbose_name = "Баннер-карусель"
        verbose_name_plural = "Баннер-карусель"


class BannerCarouselProduct(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='Уникальный идентификатор')
    bannerCarouselID = models.ForeignKey(BannerCarousel, on_delete=models.CASCADE, null=True, blank=True,
                                         related_name='bannerCarouselID',
                                         verbose_name='Идентификатор баннерной карусели')
    productCarouselID = models.ForeignKey(Products, on_delete=models.CASCADE, null=True, blank=True,
                                          related_name='bannerCarouselProduct',
                                          verbose_name='Идентификатор карусели товаров баннера')
    bannerCarouselVideo = models.FileField(upload_to="media/banner/carousel/video/", null=True, blank=True,
                                           verbose_name='Баннер-карусель Видео')
    created_at = models.DateField(auto_now_add=True, verbose_name='Дата публикации')

    def __str__(self):
        return self.bannerCarouselID.name

    class Meta:
        db_table = "banner_carousel_product"
        verbose_name = "Баннер-карусель Продукт"
        verbose_name_plural = "Баннер-карусель Продукт"
