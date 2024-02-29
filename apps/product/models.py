from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _
from ckeditor.fields import RichTextField


class ProductCategories(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Name of category'), max_length=150, null=True, blank=True)
    subcategory = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True, verbose_name="CategoryID")
    icon = models.FileField(upload_to='icon_category', null=True, blank=True, verbose_name='Icon Category')

    def __str__(self):
        return self.name

    class Meta:
        db_table = "product_category"
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"


class Products(models.Model):
    class PriceType(models.TextChoices):
        RUB = "RUB"
        USD = "USD"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Name of product'), max_length=150, null=True, blank=True)
    content = RichTextField(config_name='forum-post', extra_plugins=['someplugin'],)
    price = models.FloatField(_('Price'), default=0, null=True, blank=True)
    price_type = models.CharField(_('Type of price'), max_length=10, null=True, blank=True,
                                  choices=PriceType.choices, default=PriceType.RUB)
    categoryId = models.ForeignKey(ProductCategories, on_delete=models.CASCADE, null=True, blank=True,
                                   related_name='ProductSubCategoryID')
    image = models.ImageField(upload_to='pro_image', null=True, blank=True)
    created_at = models.DateField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "product"
        verbose_name = "Product"
        verbose_name_plural = "Products"

