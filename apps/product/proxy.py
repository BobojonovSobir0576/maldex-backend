from apps.product.models import ProductCategories


class SubCategory(ProductCategories):
    class Meta:
        proxy = True
        verbose_name = "Sub Category"
        verbose_name_plural = "Sub Categories"


class TertiaryCategory(ProductCategories):
    class Meta:
        proxy = True
        verbose_name = "Tertiary Category"
        verbose_name_plural = "Tertiary Categories"
