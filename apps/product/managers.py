from django.db import models


class CategoryManager(models.Manager):
    """Custom manager for retrieving main categories."""
    def get_queryset(self):
        """Return a queryset filtering only main categories."""
        return super().get_queryset().filter(parent=None)


class SubCategoryManager(models.Manager):
    """Custom manager for retrieving subcategories."""
    def get_queryset(self):
        """Return a queryset filtering only subcategories."""
        return super().get_queryset().filter(parent__isnull=False, parent__parent=None)


class TertiaryCategoryManager(models.Manager):
    """Custom manager for retrieving tertiary categories."""
    def get_queryset(self):
        """Return a queryset filtering only tertiary categories."""
        return super().get_queryset().filter(parent__parent__isnull=False)


class AllCategoryManager(models.Manager):
    """Custom manager for retrieving all categories."""
    def get_queryset(self):
        """Return the default queryset."""
        return super().get_queryset()
