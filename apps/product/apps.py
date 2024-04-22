from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ProductConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.product'
    verbose_name = _('product')
    verbose_name_plural = _('product')
