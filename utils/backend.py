from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q


class CustomBackend(ModelBackend):
    def authenticate(self, request, phone=None, email=None, password=None, **kwargs):
        User = get_user_model()
        query = Q()
        if phone:
            query |= Q(phone=phone)
        if email:
            query |= Q(username=email)
        try:
            user = User.objects.get(query)
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None
