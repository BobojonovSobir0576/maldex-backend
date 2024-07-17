import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from apps.auth_app.managers.user_managers import UserManager


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    first_name = models.CharField(max_length=64, null=False)
    last_name = models.CharField(max_length=64, null=False)
    email = models.EmailField('email', unique=True)
    image = models.ImageField(upload_to="user/")
    phone_number = models.CharField(max_length=128, null=True)

    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()


class UserLastLogin(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='LoginHistory')
    login_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user} logged in at {self.login_time}"

    class Meta:
        db_table = "user_last_login"
        verbose_name = "Last Login User"
        verbose_name_plural = "Last Login Users"
