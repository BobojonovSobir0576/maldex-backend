import uuid
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from apps.auth_app.managers.user_managers import CustomUserManager
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):

    class AuthType(models.TextChoices):
        LOGIN_PASSWORD_AUTH = "login_password_auth", _("Email and Password Authentication")
        GOOGLE_AUTH = "google_auth", _("Google Authentication")

    class GenderType(models.TextChoices):
        MALE = 'male', _('Male')
        FEMALE = 'female', _('Female')

    class Text:
        WRONG_PASSWORD_OR_LOGIN_ENTERED = "Wrong login or password"
        USER_WITH_SUCH_EMAIL_ALREADY_EXISTS = "A user with this email already exists"
        USER_WITH_SUCH_EMAIL_DOES_NOT_EXIST = "A user with this email already exists"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(_('Phone'), max_length=18)
    email = models.EmailField(_('Email'), max_length=255, unique=True)
    username = models.CharField(_('Username'), max_length=255, null=False, blank=False, unique=True)
    photo = models.ImageField(_('Avatar'), upload_to="path/")
    about = models.TextField(_('About yourself'), default="", null=True, blank=True)
    date_of_birth = models.DateField(_('Date of Birth'), null=True, blank=True)
    gender = models.CharField(_('Gender'), max_length=10, null=True, blank=True, choices=GenderType.choices)
    is_active = models.BooleanField(_('Is activate'), default=True)
    is_staff = models.BooleanField(_('Is staff'), default=False)
    date_joined = models.DateTimeField(_('Data created'), default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.phone

    class Meta:
        db_table = "user_table"
        verbose_name = "CustomUser"
        verbose_name_plural = "Users"


class UserLastLogin(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='LoginHistory')
    login_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user} logged in at {self.login_time}"

    class Meta:
        db_table = "user_last_login"
        verbose_name = "Last Login User"
        verbose_name_plural = "Last Login Users"
