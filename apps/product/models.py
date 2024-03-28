from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _
from ckeditor.fields import RichTextField


class ProductCategories(models.Model):
    id = models.IntegerField(primary_key=True, unique=True, blank=True, verbose_name='Уникальный идентификатор')
    name = models.CharField(max_length=150, blank=True, null=True, verbose_name="Название категории")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    is_popular = models.BooleanField(default=False, verbose_name="Популярен?")
    is_hit = models.BooleanField(default=False, verbose_name="Хит?")
    is_new = models.BooleanField(default=False, verbose_name="Новый?")
    is_available = models.BooleanField(default=False, verbose_name="Доступен на сайте?")
    icon = models.FileField(upload_to='media/category/icon/', null=True, blank=True, verbose_name='Категория значка')
    logo = models.FileField(upload_to='media/category/logo/', null=True, blank=True, verbose_name='Категория логотипа')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            # Assuming you're manually handling ID generation
            last_instance = ProductCategories.objects.all().order_by('id').last()
            next_id = 1 if not last_instance else int(last_instance.id) + 1
            self.id = f"{next_id:010d}"
        super(ProductCategories, self).save(*args, **kwargs)

    class Meta:
        db_table = "product_category"
        verbose_name = "Категория"
        verbose_name_plural = "Категория"


class Products(models.Model):
    class PriceType(models.TextChoices):
        RUB = "RUB"
        USD = "USD"

    id = models.IntegerField(primary_key=True, unique=True, blank=True, verbose_name='Уникальный идентификатор')
    name = models.CharField(_('Название продукта'), max_length=150, null=True, blank=True)
    full_name = models.CharField(_('Полное Название продукта'), max_length=255, null=True, blank=True)
    brand = models.CharField(_('Бренд'), max_length=155, null=True, blank=True)
    article = models.CharField(_('Артикул'), max_length=155, null=True, blank=True)
    price = models.FloatField(_('Цена'), default=0, null=True, blank=True)
    price_type = models.CharField(_('Цена валюта'), max_length=10, null=True, blank=True,
                                  choices=PriceType.choices, default=PriceType.RUB)
    categoryId = models.ForeignKey(ProductCategories, on_delete=models.CASCADE, null=True, blank=True,
                                   related_name='ProductSubCategoryID', verbose_name='Категория продукта')
    description = models.TextField(null=True, blank=True, verbose_name='Описания')
    image = models.ImageField(upload_to='main-image', null=True, blank=True, verbose_name='Главное фото')
    attributes = models.JSONField(null=True, blank=True, verbose_name='Атрибуты')
    included_branding = models.JSONField(null=True, blank=True, verbose_name='Включенный брендинг')
    discount_price = models.FloatField(default=0, null=True, blank=True, verbose_name='Цена со скидкой')
    is_popular = models.BooleanField(default=False, verbose_name="Популярен?")
    is_hit = models.BooleanField(default=False, verbose_name="Хит?")
    is_new = models.BooleanField(default=False, verbose_name="Новый?")
    created_at = models.DateField(auto_now_add=True, blank=True, null=True, verbose_name='Данные опубликованы')

    def save(self, *args, **kwargs):
        if not self.id:
            # Assuming you're manually handling ID generation
            last_instance = Products.objects.all().order_by('id').last()
            next_id = 1 if not last_instance else int(last_instance.id) + 1
            self.id = f"{next_id:010d}"
        super(Products, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "product"
        verbose_name = "Продукт"
        verbose_name_plural = "Продукт"


class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='Уникальный идентификатор')
    productID = models.ForeignKey('Products', on_delete=models.CASCADE, null=True, blank=True, related_name='productID',
                                  verbose_name='Код товара')
    big = models.ImageField(upload_to='product/images/big', null=True, blank=True, verbose_name='Большой Изображений')
    big_url = models.URLField(max_length=1024, null=True, blank=True, verbose_name='URL большого изображения')

    small = models.ImageField(upload_to='product/images/small', null=True, blank=True,
                              verbose_name='Маленький Изображений')
    small_url = models.URLField(max_length=1024, null=True, blank=True, verbose_name='URL маленького изображения')

    superbig = models.ImageField(upload_to='product/images/superbig', null=True, blank=True,
                                 verbose_name='Супербольшой Изображений')
    superbig_url = models.URLField(max_length=1024, null=True, blank=True, verbose_name='URL супербольшого изображения')

    thumbnail = models.ImageField(upload_to='product/images/thumbnail', null=True, blank=True,
                                  verbose_name='Миниатюра Изображений')
    thumbnail_url = models.URLField(max_length=1024, null=True, blank=True, verbose_name='URL миниатюры изображения')
    def __str__(self):
        return self.productID.name

    def __str__(self):
        return self.productID.name if self.productID and hasattr(self.productID, 'name') else str(self.id)

    class Meta:
        db_table = "product_images"
        verbose_name = "Изображения продукта"
        verbose_name_plural = "Изображения продукта"


class Colors(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='Уникальный идентификатор')
    name = models.CharField(_('Название цвета'), max_length=50, null=True, blank=True)
    image = models.ImageField(upload_to='colors', null=True, blank=True, verbose_name='Изображение')

    def __str__(self):
        return self.name

    class Meta:
        db_table = "product_color"
        verbose_name = "Цвет"
        verbose_name_plural = "Цвет"


