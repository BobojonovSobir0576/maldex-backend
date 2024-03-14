from apps.product.models import ProductCategories


class SubCategory(ProductCategories):
    class Meta:
        proxy = True
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"


class TertiaryCategory(ProductCategories):
    class Meta:
        proxy = True
        verbose_name = "Третичная категория"
        verbose_name_plural = "Третичные категории"
