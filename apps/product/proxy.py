from apps.product.managers import SubCategoryManager, TertiaryCategoryManager
from apps.product.models import ProductCategories


class SubCategory(ProductCategories):
    objects = SubCategoryManager()

    class Meta:
        proxy = True
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"


class TertiaryCategory(ProductCategories):
    objects = TertiaryCategoryManager()
    
    class Meta:
        proxy = True
        verbose_name = "Третичная категория"
        verbose_name_plural = "Третичные категории"
