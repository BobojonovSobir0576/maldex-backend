from django.contrib.auth.backends import ModelBackend

from apps.user.models import User


class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        email = email or kwargs.get('username', None)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None
