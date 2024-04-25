from apps.product.managers import SubCategoryManager, TertiaryCategoryManager
from apps.product.models import ProductCategories


class SubCategory(ProductCategories):
    """Proxy model representing subcategories."""
    objects = SubCategoryManager()  # Custom manager for SubCategory

    class Meta:
        proxy = True  # Specifies that this is a proxy model
        verbose_name = "Подкатегория"  # Singular name for display in the admin interface
        verbose_name_plural = "Подкатегории"  # Plural name for display in the admin interface


class TertiaryCategory(ProductCategories):
    """Proxy model representing tertiary categories."""
    objects = TertiaryCategoryManager()  # Custom manager for TertiaryCategory

    class Meta:
        proxy = True  # Specifies that this is a proxy model
        verbose_name = "Третичная категория"  # Singular name for display in the admin interface
        verbose_name_plural = "Третичные категории"  # Plural name for display in the admin interface
