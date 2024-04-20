from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _

from apps.product.managers import AllCategoryManager


class ProductCategories(models.Model):
    id = models.IntegerField(primary_key=True, editable=False, unique=True, verbose_name='Уникальный идентификатор')
    order = models.PositiveSmallIntegerField(null=True, blank=True)
    name = models.CharField(max_length=150, verbose_name="Название категории")
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    slug = models.SlugField(max_length=255, null=True, blank=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    is_popular = models.BooleanField(default=False, verbose_name="Популярен?")
    is_hit = models.BooleanField(default=False, verbose_name="Хит?")
    is_new = models.BooleanField(default=False, verbose_name="Новый?")
    is_available = models.BooleanField(default=True, verbose_name="Доступен на сайте?")
    icon = models.FileField(upload_to='icon/', null=True, blank=True, verbose_name='Категория значка')
    logo = models.FileField(upload_to='logo/', null=True, blank=True, verbose_name='Категория логотипа')

    objects = AllCategoryManager()
    all_levels = AllCategoryManager()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            last_instance = ProductCategories.all_levels.all().order_by('id').last()
            next_id = 1 if not last_instance else int(last_instance.id) + 1
            self.id = f"{next_id:010d}"

        if not self.order:
            last_instance = ProductCategories.objects.filter(parent=None).order_by('order').last()
            next_id = 1 if not (last_instance and last_instance.order) else last_instance.order + 1
            self.order = next_id
        super(ProductCategories, self).save(*args, **kwargs)

    class Meta:
        db_table = "product_category"
        verbose_name = "Категория"
        verbose_name_plural = "Категория"


class ExternalCategory(models.Model):
    external_id = models.CharField(max_length=255)
    category = models.ForeignKey(ProductCategories, on_delete=models.CASCADE, related_name='external_categories',)

    class Meta:
        unique_together = ('external_id', 'category')
        db_table = "product_site_category"
        verbose_name = "Site Category"
        verbose_name_plural = "Site Categories "


class Products(models.Model):
    id = models.IntegerField(primary_key=True, unique=True, blank=True, verbose_name='Уникальный идентификатор')
    name = models.CharField(_('Название продукта'), max_length=150)
    code = models.IntegerField(default=0)
    article = models.CharField(_('Артикул'), max_length=155)
    product_size = models.CharField(_('Размер товара'), max_length=155, default="S-XXL")
    material = models.CharField(_('Материал'), max_length=155, default="S-XXL")
    description = models.TextField(verbose_name='Описания')
    brand = models.CharField(_('Бренд'), max_length=155, null=True, blank=True)
    price = models.FloatField(_('Цена'), default=0)
    price_type = models.CharField(_('Цена валюта'), max_length=10,
                                  choices=[('RUB', 'RUB'), ('USD', 'USD')], default='RUB')
    discount_price = models.FloatField(default=None, null=True, blank=True, verbose_name='Цена со скидкой')
    categoryId = models.ForeignKey(ProductCategories, on_delete=models.CASCADE, null=True, blank=True,
                                   related_name='ProductSubCategoryID', verbose_name='Категория продукта')
    weight = models.CharField(_('Масса'), max_length=155, null=True, blank=True)
    barcode = models.CharField(_('Штрих-код продукта'), max_length=155, null=True, blank=True)
    ondemand = models.BooleanField(default=True)
    moq = models.CharField(default='0', max_length=256, null=True, blank=True)
    days = models.IntegerField(default=0, null=True, blank=True)
    pack = models.JSONField(null=True, blank=True)
    is_popular = models.BooleanField(default=False, verbose_name="Популярен?")
    is_hit = models.BooleanField(default=False, verbose_name="Хит?")
    is_new = models.BooleanField(default=False, verbose_name="Новый?")
    created_at = models.DateField(auto_now_add=True, verbose_name='Данные опубликованы')

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


class Colors(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='Уникальный идентификатор')
    name = models.CharField(_('Название цвета'), max_length=50)
    image = models.ImageField(upload_to='colors/', null=True, blank=True, verbose_name='Изображение')

    def __str__(self):
        return self.name

    class Meta:
        db_table = "product_color"
        verbose_name = "Цвет"
        verbose_name_plural = "Цвет"


class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='Уникальный идентификатор')
    productID = models.ForeignKey('Products', on_delete=models.CASCADE, null=True, blank=True,
                                  related_name='images_set', verbose_name='Код товара')
    image = models.ImageField(upload_to='media/product/', verbose_name="изображения", null=True, blank=True)
    image_url = models.URLField(max_length=1024, null=True, blank=True, verbose_name='URL изображения')
    colorID = models.ForeignKey(Colors, on_delete=models.CASCADE, verbose_name='Цвета')

    def __str__(self):
        return self.productID.name if self.productID and hasattr(self.productID, 'name') else str(self.id)

    class Meta:
        db_table = "product_images"
        verbose_name = "Изображения продукта"
        verbose_name_plural = "Изображения продукта"
