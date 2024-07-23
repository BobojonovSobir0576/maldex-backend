import uuid
from django.utils.translation import gettext_lazy as _
from django.db import models
from apps.product.models import Products


class Banner(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='Уникальный идентификатор')
    name = models.CharField(_('Название баннера'), max_length=155)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    order_by_id = models.IntegerField(default=0, null=True, blank=True, verbose_name="Order By ID")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.order_by_id:
            if Banner.objects.last():
                order = Banner.objects.last().order_by_id + 1
                self.order_by_id = order
            else:
                self.order_by_id = 1
        return super().save(*args, **kwargs)

    class Meta:
        db_table = "banner"
        ordering = ['order_by_id']
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
    media = models.FileField(upload_to='banner_carousel/')
    media_type = models.CharField(max_length=255)
    product = models.ForeignKey(Products, on_delete=models.CASCADE, null=True, blank=True,)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')

    def __str__(self):
        return self.name

    class Meta:
        db_table = "banner_carousel"
        verbose_name = "Баннер-карусель"
        verbose_name_plural = "Баннер-карусель"


class Button(models.Model):
    title = models.CharField(max_length=512)
    url = models.CharField(max_length=512)
    banner_carousel = models.ForeignKey(BannerCarousel, on_delete=models.CASCADE, related_name='buttons')
