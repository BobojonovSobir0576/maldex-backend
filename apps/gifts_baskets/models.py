from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.product.models import Products


class GiftsBasketCategory(models.Model):
    name = models.CharField(max_length=150, blank=True, null=True, verbose_name="Название категории")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    is_available = models.BooleanField(default=False, verbose_name="Доступен на сайте?")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "gifts_basket_category"
        verbose_name = "Подарочные наборы Категория"
        verbose_name_plural = "Подарочные наборы Категория"


class GiftsBaskets(models.Model):
    title = models.CharField(_(''), max_length=255, null=True, blank=True)
    small_header = models.TextField(null=True, blank=True, verbose_name="")
    article = models.CharField(_('Артикул'), max_length=155, null=True, blank=True)
    description = models.TextField(verbose_name='', null=True, blank=True)
    gift_basket_category = models.ManyToManyField(GiftsBasketCategory, null=True, blank=True, related_name='cateGiftBasket')
    other_sets = models.JSONField(null=True, blank=True, verbose_name='')
    price = models.FloatField(_('Цена'), default=0, null=True, blank=True)
    price_type = models.CharField(_('Цена валюта'), max_length=10, null=True, blank=True)
    discount_price = models.FloatField(default=0, null=True, blank=True, verbose_name='Цена со скидкой')
    created_at = models.DateField(auto_now_add=True, blank=True, null=True, verbose_name='Данные опубликованы')

    def __str__(self):
        return self.title

    class Meta:
        db_table = "gifts_basket"
        verbose_name = "Подарочные наборы"
        verbose_name_plural = "Подарочные наборы"


class GiftsBasketImages(models.Model):
    gift_basket = models.ForeignKey(GiftsBaskets, on_delete=models.CASCADE,
                                    null=True, blank=True, related_name='basket_images')
    images = models.ImageField(upload_to='gift_basket/', null=True, blank=True)

    def __str__(self):
        return self.gift_basket.title

    class Meta:
        db_table = "gifts_basket_image"
        verbose_name = "Подарочные наборы изображения"
        verbose_name_plural = "Подарочные наборы изображения"


class GiftsBasketProduct(models.Model):
    gift_basket = models.ForeignKey(GiftsBaskets, on_delete=models.CASCADE, related_name='basket_products',
                                    null=True, blank=True, )
    product_sets = models.ForeignKey(Products, on_delete=models.CASCADE,  null=True, blank=True)
    quantity = models.IntegerField(default=0, null=True, blank=True, verbose_name='')

    def __str__(self):
        return self.gift_basket.title

    class Meta:
        db_table = "gifts_basket_product"
        verbose_name = "Подарочные наборы товара"
        verbose_name_plural = "Подарочные наборы товара"

