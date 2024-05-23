from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.product.models import Products


class TagCategory(models.Model):
    name = models.CharField(_('Название'), max_length=150)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "teg_category"
        verbose_name = "Тег категории"
        verbose_name_plural = "Тег категории"


class Tag(models.Model):
    name = models.CharField(_('Название тэга'), max_length=50)
    order = models.IntegerField(blank=True)
    tag_category = models.ForeignKey(TagCategory, on_delete=models.CASCADE, null=True, blank=True,
                                     related_name='categoryTag')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Теги"
        verbose_name_plural = "Теги"
    #
    # def save(self, *args, **kwargs):
    #     last_tag = Tag.objects.all().order_by('order').last()
    #     self.order = last_tag.order + 1 if last_tag else 1
    #     return super().save(*args, **kwargs)


class GiftsBasketCategory(models.Model):
    name = models.CharField(_('Название категории подарочной корзины'), max_length=150,
                            blank=True, null=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    is_available = models.BooleanField(default=False, verbose_name="Доступен на сайте?")

    # def __str__(self):
    #     return self.name

    class Meta:
        db_table = "gifts_basket_category"
        verbose_name = "Подарочные наборы Категория"
        verbose_name_plural = "Подарочные наборы Категория"


class GiftsBaskets(models.Model):
    title = models.CharField(_('Название подарочной корзины'), max_length=255, null=True, blank=True)
    small_header = models.TextField(_('Назовите небольшой заголовок подарочной корзины.'), null=True, blank=True)
    article = models.CharField(_('Артикул'), max_length=155, null=True, blank=True)
    description = models.TextField(verbose_name='Описание', null=True, blank=True)
    gift_basket_category = models.ManyToManyField(GiftsBasketCategory, blank=True, related_name='cateGiftBasket')
    other_sets = models.JSONField(null=True, blank=True, verbose_name='Другие наборы')
    price = models.FloatField(_('Цена'), default=0, null=True, blank=True)
    price_type = models.CharField(_('Цена валюта'), max_length=10, null=True, blank=True)
    discount_price = models.FloatField(default=0, null=True, blank=True, verbose_name='Цена со скидкой')
    created_at = models.DateField(auto_now_add=True, null=True, blank=True, verbose_name='Дата публикации')
    tags = models.ManyToManyField(Tag, related_name='baskets', verbose_name='Бирки для корзины подарков')

    def __str__(self):
        return self.title

    class Meta:
        db_table = "gifts_basket"
        verbose_name = "Подарочные наборы"
        verbose_name_plural = "Подарочные наборы"


class GiftsBasketImages(models.Model):
    gift_basket = models.ForeignKey(GiftsBaskets, on_delete=models.CASCADE,
                                    null=True, blank=True, related_name='basket_images')
    images = models.ImageField(upload_to='gift_basket/', null=True, blank=True, verbose_name='Изображений')

    def __str__(self):
        return self.gift_basket.title

    class Meta:
        db_table = "gifts_basket_image"
        verbose_name = "Подарочные наборы изображения"
        verbose_name_plural = "Подарочные наборы изображения"


class GiftsBasketProduct(models.Model):
    gift_basket = models.ForeignKey(GiftsBaskets, on_delete=models.CASCADE, related_name='basket_products',
                                    null=True, blank=True, )
    product_sets = models.ForeignKey(Products, on_delete=models.CASCADE,  null=True, blank=True,
                                     verbose_name='Наборы продуктов')
    quantity = models.IntegerField(default=0, null=True, blank=True, verbose_name='Количество')

    def __str__(self):
        return self.gift_basket.title

    class Meta:
        db_table = "gifts_basket_product"
        verbose_name = "Подарочные наборы товара"
        verbose_name_plural = "Подарочные наборы товара"


class SetCategory(models.Model):
    title = models.CharField(_('Название'), max_length=255, null=True, blank=True)
    is_available = models.BooleanField(default=False, verbose_name="Доступен на сайте?")
    created_at = models.DateField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return 'hello'

    class Meta:
        db_table = "set_category"
        verbose_name = "Каталог наборов"
        verbose_name_plural = "Каталог наборов"


class SetProducts(models.Model):
    set_category = models.ForeignKey(SetCategory, on_delete=models.CASCADE, null=True, blank=True,
                                     related_name='setProducts')
    product_sets = models.ForeignKey(Products, on_delete=models.CASCADE,  null=True, blank=True,
                                     verbose_name='Наборы продуктов')
    quantity = models.IntegerField(default=0, null=True, blank=True, verbose_name='Количество')
    created_at = models.DateField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.set_category.title

    class Meta:
        db_table = "set_product"
        verbose_name = "Наборы Каталог товаров"
        verbose_name_plural = "Наборы Каталог товаров"


class AdminFiles(models.Model):
    name = models.CharField(max_length=150, blank=True, null=True, verbose_name="Название")
    file = models.FileField(upload_to='files/', null=True, blank=True, verbose_name='File')
    created_at = models.DateField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "admin_files"
        verbose_name = "Административные файлы"
        verbose_name_plural = "Административные файлы"
