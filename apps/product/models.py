from django.contrib.auth import get_user_model
from django.db import models
import uuid

from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.product.managers import AllCategoryManager

User = get_user_model()


class ProductCategories(models.Model):
    """Model to represent product categories."""
    id = models.IntegerField(primary_key=True, editable=False, unique=True, verbose_name='Уникальный идентификатор')
    name = models.CharField(max_length=550, verbose_name="Название категории")
    title = models.CharField(max_length=500, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    slug = models.SlugField(max_length=500, null=True, blank=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")

    is_popular = models.BooleanField(default=False, verbose_name="Популярен?")
    is_hit = models.BooleanField(default=False, verbose_name="Хит?")
    is_new = models.BooleanField(default=False, verbose_name="Новый?")
    is_available = models.BooleanField(default=False, verbose_name="Доступен на сайте?")

    icon = models.FileField(upload_to='icon/', null=True, blank=True, verbose_name='Категория значка')
    logo = models.FileField(upload_to='logo/', null=True, blank=True, verbose_name='Категория логотипа')
    site = models.CharField(max_length=500, null=True, blank=True)
    seo_title = models.CharField(max_length=500, null=True, blank=True, verbose_name='SEO Заголовок')
    seo_description = models.TextField(null=True, blank=True, verbose_name='SEO Описание')

    order = models.PositiveSmallIntegerField(null=True, blank=True)
    order_top = models.PositiveSmallIntegerField(null=True, blank=True)
    order_by_site = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Порядок сайта')
    home = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    products_count = models.IntegerField(default=0)
    recently_products_count = models.IntegerField(default=0)
    discounts = models.JSONField(null=True, blank=True)

    objects = AllCategoryManager()
    all_levels = AllCategoryManager()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Override save method to generate ID and order if not provided."""
        if not self.id:
            last_instance = ProductCategories.objects.all().order_by('id').last()
            next_id = 1 if not last_instance else last_instance.id + 1
            self.id = next_id

        if not self.order and self.is_available and self.parent is None:
            popular_categories = ProductCategories.objects.filter(is_available=True, parent=None).order_by('order')
            self.order = (popular_categories.last().order + 1) if popular_categories.exists() else 1

        if not self.order_top and self.is_available and self.is_popular and self.parent is None:
            popular_categories = ProductCategories.objects.filter(
                is_popular=True, is_available=True, parent=None).order_by('order_top')
            self.order_top = (popular_categories.last().order_top + 1) if popular_categories.exists() else 1

        super().save(*args, **kwargs)

    class Meta:
        db_table = "product_category"
        ordering = ('-is_available', 'order', 'order_by_site')
        verbose_name = "Категория"
        verbose_name_plural = "Категория"


@receiver(pre_save, sender=ProductCategories)
def pre_save_category(sender, instance, **kwargs):
    old = ProductCategories.objects.filter(pk=instance.pk).first()
    previous = ProductCategories.objects.filter(order_top=instance.order_top).first()
    previous_by_order = ProductCategories.objects.filter(order=instance.order).first()
    if old and previous and previous.order_top != old.order_top and previous.order_top is not None:
        ProductCategories.objects.filter(pk=previous.pk).update(order_top=old.order_top)
    if old and previous_by_order and previous_by_order.order != old.order and previous_by_order.order is not None:
        ProductCategories.objects.filter(pk=previous_by_order.pk).update(order=old.order)


@receiver(post_save, sender=ProductCategories)
def post_save_category(sender, instance, **kwargs):
    top_categories = ProductCategories.objects.filter(is_available=True, is_popular=True, parent=None).order_by(
        'order_top')
    for num, category in enumerate(top_categories):
        ProductCategories.objects.filter(pk=category.pk).update(order_top=num + 1)
    ProductCategories.objects.filter(is_popular=False, parent=None).update(order_top=None)

    ava_categories = ProductCategories.objects.filter(is_available=True, parent=None).order_by('order')
    for num, category in enumerate(ava_categories):
        ProductCategories.objects.filter(pk=category.pk).update(order=num+1)
    ProductCategories.objects.filter(is_available=False, parent=None).update(order=None)


class ExternalCategory(models.Model):
    """Model to represent external categories."""
    external_id = models.CharField(max_length=500, verbose_name='внешний идентификатор')
    category = models.ForeignKey(ProductCategories, on_delete=models.CASCADE, related_name='external_categories',
                                 verbose_name='категория')

    class Meta:
        unique_together = ('external_id', 'category')
        db_table = "product_site_category"
        verbose_name = "Категория сайта"
        verbose_name_plural = "Категории сайта"


class Colors(models.Model):
    """Model to represent colors."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='Уникальный идентификатор')
    name = models.CharField(_('Название цвета'), max_length=500)
    hex = models.CharField(max_length=16, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "product_color"
        verbose_name = "Цвет"
        verbose_name_plural = "Цвет"


class Products(models.Model):
    """Model to represent products."""
    id = models.BigIntegerField(primary_key=True, unique=True, blank=True, verbose_name='Уникальный идентификатор')
    name = models.CharField(_('Название продукта'), max_length=512, null=True, blank=True)
    code = models.IntegerField(default=0, null=True, blank=True)
    group = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    article = models.CharField(_('Артикул'), max_length=512, null=True, blank=True)
    product_size = models.CharField(_('Размер товара'), max_length=256, null=True, blank=True)
    material = models.CharField(_('Материал'), max_length=512, default="S-XXL", null=True, blank=True)
    description = models.TextField(verbose_name='Описания', null=True, blank=True)
    brand = models.CharField(_('Бренд'), max_length=500, null=True, blank=True)
    price = models.FloatField(_('Цена'), default=0, null=True, blank=True)
    price_type = models.CharField(_('Цена валюта'), max_length=10,
                                  choices=[('RUB', 'RUB'), ('USD', 'USD')], default='RUB', null=True, blank=True)
    discount_price = models.FloatField(default=None, null=True, blank=True, verbose_name='Цена со скидкой')
    categoryId = models.ForeignKey(ProductCategories, on_delete=models.CASCADE, null=True, blank=True,
                                   related_name='products', verbose_name='Категория продукта', db_index=True)
    weight = models.CharField(_('Масса'), max_length=128, null=True, blank=True)
    barcode = models.CharField(_('Штрих-код продукта'), max_length=128, null=True, blank=True)
    ondemand = models.BooleanField(default=True, null=True, blank=True)
    moq = models.CharField(default='0', max_length=512, null=True, blank=True)
    days = models.IntegerField(default=0, null=True, blank=True)
    pack = models.JSONField(null=True, blank=True)
    prints = models.JSONField(null=True, blank=True)
    warehouse = models.JSONField(null=True, blank=True)
    colorID = models.ForeignKey(Colors, on_delete=models.CASCADE, verbose_name='Цвета', related_name='products', null=True)
    sizes = models.JSONField(null=True, blank=True)
    is_popular = models.BooleanField(default=False, verbose_name="Популярен?", null=True, blank=True)
    is_hit = models.BooleanField(default=False, verbose_name="Хит?", null=True, blank=True)
    is_new = models.BooleanField(default=False, verbose_name="Новый?", null=True, blank=True)
    site = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Данные опубликованы')
    updated_at = models.DateTimeField(auto_now=True)
    home = models.BooleanField(default=False)
    discounts = models.JSONField(null=True, blank=True)
    common_name = models.CharField(max_length=500, null=True, blank=True, db_index=True)

    added_recently = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.common_name:
            color_name = self.colorID.name.lower()
            product_name = self.name.replace('\xa0', ' ').lower()
            without_color_name = product_name[:product_name.index(color_name)] if color_name in product_name else product_name
            space_index = without_color_name[::-1].find(' ')
            self.common_name = without_color_name[:- space_index - 1] if len(self.name.split()) > 1 and color_name in product_name else product_name

        if not self.id:
            last_instance = Products.objects.all().order_by('id').last()
            next_id = 1 if not last_instance else int(last_instance.id) + 1
            self.id = f"{next_id:010d}"

        category = self.categoryId
        while category:
            category.products_count = Products.objects.filter(
                Q(categoryId=category) | Q(categoryId__parent=category) |
                Q(categoryId__parent__parent=category)
            ).count()
            category.recently_products_count = Products.objects.filter(
                Q(categoryId=category) | Q(categoryId__parent=category) |
                Q(categoryId__parent__parent=category), added_recently=True
            ).count()
            category.save()
            category = category.parent
        super(Products, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "product"
        ordering = ('-updated_at',)
        verbose_name = "Продукт"
        verbose_name_plural = "Продукт"


class ProductImage(models.Model):
    """Model to represent product images."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='Уникальный идентификатор')
    productID = models.ForeignKey('Products', on_delete=models.CASCADE, null=True, blank=True,
                                  related_name='images_set', verbose_name='Код товара')
    image = models.ImageField(upload_to='media/product/', verbose_name="изображения", null=True, blank=True)
    image_url = models.URLField(max_length=1024, null=True, blank=True, verbose_name='URL изображения')

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


class SiteLogo(models.Model):
    site = models.CharField(max_length=256)
    logo = models.ImageField(upload_to='site_logos/')

    class Meta:
        db_table = 'site_logos'
        verbose_name = 'Site Logo'
        verbose_name_plural = 'Site Logos'

    def __str__(self):
        return self.site


class ProductBanner(models.Model):
    title = models.CharField(max_length=512)
    subtitle = models.CharField(max_length=1024)
    image = models.ImageField(upload_to='product-banners/')
    button_title = models.CharField(max_length=128)
    button_url = models.URLField()

    class Meta:
        db_table = 'product_banners'
        verbose_name = 'product banner'
        verbose_name_plural = 'product banners'

    def __str__(self):
        return self.title


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        db_table = 'likes'
        verbose_name = 'Like'
        verbose_name_plural = 'Likes'
