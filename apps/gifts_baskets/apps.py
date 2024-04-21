from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GiftsBasketsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.gifts_baskets'
    verbose_name = _('Gift Basket')
    verbose_name_plural = _('Gift Basket')
