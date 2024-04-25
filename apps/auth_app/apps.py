from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AuthAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.auth_app'
    verbose_name = _('аутентификация')
