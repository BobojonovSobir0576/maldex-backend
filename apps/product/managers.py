from django.db import models


class CategoryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(parent=None)


class SubCategoryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(parent__isnull=False, parent__parent=None)


class TertiaryCategoryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(parent__parent__isnull=False)


class AllCategoryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()
