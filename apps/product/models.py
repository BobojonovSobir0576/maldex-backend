from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _

from apps.product.managers import AllCategoryManager


class ProductCategories(models.Model):
    """Model to represent product categories."""
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
    site = models.CharField(max_length=255, null=True, blank=True)
    home = models.BooleanField(default=False,)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    objects = AllCategoryManager()
    all_levels = AllCategoryManager()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Override save method to generate ID and order if not provided."""
        if not self.id:
            last_instance = ProductCategories.all_levels.all().order_by('id').last()
            next_id = 1 if not last_instance else int(last_instance.id) + 1
            self.id = f"{next_id:010d}"
        if not self.order:
            last_instance = ProductCategories.objects.filter(parent=self.parent, is_available=True).order_by('order').last()
            next_id = 1 if not (last_instance and last_instance.order) else last_instance.order + 1
            self.order = next_id
        elif not self.is_available:
            self.order = None

        print(self, self.order)

        super(ProductCategories, self).save(*args, **kwargs)

    class Meta:
        db_table = "product_category"
        ordering = ('-is_available', 'order')
        verbose_name = "Категория"
        verbose_name_plural = "Категория"


class ExternalCategory(models.Model):
    """Model to represent external categories."""
    external_id = models.CharField(max_length=255, verbose_name='внешний идентификатор')
    category = models.ForeignKey(ProductCategories, on_delete=models.CASCADE, related_name='external_categories',
                                 verbose_name='категория')

    class Meta:
        unique_together = ('external_id', 'category')
        db_table = "product_site_category"
        verbose_name = "Категория сайта"
        verbose_name_plural = "Категории сайта"


class Products(models.Model):
    """Model to represent products."""
    id = models.BigIntegerField(primary_key=True, unique=True, blank=True, verbose_name='Уникальный идентификатор')
    name = models.CharField(_('Название продукта'), max_length=512, null=True, blank=True)
    code = models.IntegerField(default=0, null=True, blank=True)
    article = models.CharField(_('Артикул'), max_length=512, null=True, blank=True)
    product_size = models.CharField(_('Размер товара'), max_length=256, default="S-XXL", null=True, blank=True)
    material = models.CharField(_('Материал'), max_length=512, default="S-XXL", null=True, blank=True)
    description = models.TextField(verbose_name='Описания', null=True, blank=True)
    brand = models.CharField(_('Бренд'), max_length=128, null=True, blank=True)
    price = models.FloatField(_('Цена'), default=0, null=True, blank=True)
    price_type = models.CharField(_('Цена валюта'), max_length=10,
                                  choices=[('RUB', 'RUB'), ('USD', 'USD')], default='RUB', null=True, blank=True)
    discount_price = models.FloatField(default=None, null=True, blank=True, verbose_name='Цена со скидкой')
    categoryId = models.ForeignKey(ProductCategories, on_delete=models.CASCADE, null=True, blank=True,
                                   related_name='ProductSubCategoryID', verbose_name='Категория продукта')
    weight = models.CharField(_('Масса'), max_length=128, null=True, blank=True)
    barcode = models.CharField(_('Штрих-код продукта'), max_length=128, null=True, blank=True)
    ondemand = models.BooleanField(default=True, null=True, blank=True)
    moq = models.CharField(default='0', max_length=512, null=True, blank=True)
    days = models.IntegerField(default=0, null=True, blank=True)
    quantity = models.CharField(max_length=252, null=True, blank=True)
    pack = models.JSONField(null=True, blank=True)
    prints = models.JSONField(null=True, blank=True)
    is_popular = models.BooleanField(default=False, verbose_name="Популярен?", null=True, blank=True)
    is_hit = models.BooleanField(default=False, verbose_name="Хит?", null=True, blank=True)
    is_new = models.BooleanField(default=False, verbose_name="Новый?", null=True, blank=True)
    site = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Данные опубликованы')
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """Override save method to generate ID."""
        if not self.id:
            last_instance = Products.objects.all().order_by('id').last()
            next_id = 1 if not last_instance else int(last_instance.id) + 1
            self.id = f"{next_id:010d}"
        super(Products, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "product"
        ordering = ('-updated_at',)
        verbose_name = "Продукт"
        verbose_name_plural = "Продукт"


class Colors(models.Model):
    """Model to represent colors."""
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
    """Model to represent product images."""
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


class ProductFilterModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='Уникальный идентификатор')
    title = models.CharField(max_length=255)
    created_at = models.DateField(auto_now_add=True, verbose_name='Дата публикации')

    class Meta:
        db_table = "filter_for_product"
        verbose_name = "фильтр для продукта"
        verbose_name_plural = "фильтры для продукта"


class ProductFilterProducts(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='Уникальный идентификатор')
    filter = models.ForeignKey(ProductFilterModel, on_delete=models.CASCADE, related_name='products')
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='filter_products')
    created_at = models.DateField(auto_now_add=True, verbose_name='Дата публикации')

    class Meta:
        db_table = "filter_for_product_products"
        verbose_name = "фильтрует продукты по продукту"
        verbose_name_plural = "фильтрует продукты по продукту"
