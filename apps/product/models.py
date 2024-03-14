from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _
from ckeditor.fields import RichTextField


class ProductCategories(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='Уникальный идентификатор')
    name = models.CharField(max_length=150, blank=True, null=True, verbose_name="Название категории")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    is_popular = models.BooleanField(default=False, verbose_name="Популярен?")
    is_hit = models.BooleanField(default=False, verbose_name="Хит?")
    is_new = models.BooleanField(default=False, verbose_name="Новый?")
    icon = models.FileField(upload_to='media/category/icon/', null=True, blank=True, verbose_name='Категория значка')
    logo = models.FileField(upload_to='media/category/logo/', null=True, blank=True, verbose_name='Категория логотипа')

    def __str__(self):
        return self.name

    def category_hierarchy(self):
        """Returns a string representation of the category hierarchy."""
        ancestors = [self.name]
        parent = self.parent
        while parent is not None:
            ancestors.insert(0, parent.name)
            parent = parent.parent
        return " > ".join(ancestors)

    class Meta:
        db_table = "product_category"
        verbose_name = "Категория"
        verbose_name_plural = "Категория"


class Products(models.Model):
    class PriceType(models.TextChoices):
        RUB = "RUB"
        USD = "USD"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='Уникальный идентификатор')
    vendor_code = models.CharField(_('Артикул'), max_length=155, null=True, blank=True)
    name = models.CharField(_('Название продукта'), max_length=150, null=True, blank=True)
    content = RichTextField(config_name='forum-post', extra_plugins=['someplugin'], verbose_name='Описания')
    price = models.FloatField(_('Цена'), default=0, null=True, blank=True)
    price_type = models.CharField(_('Цена валюта'), max_length=10, null=True, blank=True,
                                  choices=PriceType.choices, default=PriceType.RUB)
    image = models.ImageField(upload_to='main-image', null=True, blank=True, verbose_name='Главное фото')
    brand = models.CharField(_('Бренд'), max_length=155, null=True, blank=True)
    material = models.CharField(_('Материал'), max_length=155, null=True, blank=True)
    gross_weight = models.IntegerField(default=0, null=True, blank=True, verbose_name='Вес брутто')
    dimensions = models.CharField(_('Размеры'), max_length=100, blank=True, null=True)
    package_dimensions = models.CharField(_('Размеры упаковки'), max_length=100, blank=True, null=True)
    package_quantity = models.CharField(_('Количество упаковки'), max_length=100, blank=True, null=True)
    package_wight = models.CharField(_('Вес упаковки'), max_length=100, blank=True, null=True)
    categoryId = models.ForeignKey(ProductCategories, on_delete=models.CASCADE, null=True, blank=True,
                                   related_name='ProductSubCategoryID', verbose_name='Категория продукта')
    is_popular = models.BooleanField(default=False, verbose_name="Популярен?")
    is_hit = models.BooleanField(default=False, verbose_name="Хит?")
    is_new = models.BooleanField(default=False, verbose_name="Новый?")
    created_at = models.DateField(auto_now_add=True, blank=True, null=True, verbose_name='Данные опубликованы')

    def __str__(self):
        return self.name

    class Meta:
        db_table = "product"
        verbose_name = "Продукт"
        verbose_name_plural = "Продукт"


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


class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='Уникальный идентификатор')
    productID = models.ForeignKey(Products, on_delete=models.CASCADE, null=True, blank=True,
                                  related_name='productID', verbose_name='Код товара')
    images = models.ImageField(upload_to='product/images', null=True, blank=True, verbose_name='Изображений')
    color = models.ForeignKey(Colors, on_delete=models.CASCADE, null=True, blank=True,
                              related_name='colorProduct', verbose_name='Цвет')

    def __str__(self):
        return self.productID.name

    class Meta:
        db_table = "product_images"
        verbose_name = "Изображения продукта"
        verbose_name_plural = "Изображения продукта"