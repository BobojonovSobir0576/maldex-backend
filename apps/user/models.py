from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.user.managers import UserManager


class User(AbstractUser):
    first_name = models.CharField(max_length=64, null=False)
    last_name = models.CharField(max_length=64, null=False)
    email = models.EmailField('email', unique=True)
    image = models.ImageField(upload_to="user/")

    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()
