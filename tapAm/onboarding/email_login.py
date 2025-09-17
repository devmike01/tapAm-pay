from django.contrib.auth import get_user
from django.contrib.auth.backends import ModelBackend

from .model_manager import CustomUserManager
from .models import UserProfile


class EmailLogin(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        #user_model = get_user(request)
        try:
            user = UserProfile.objects.get(email=username)
        except UserProfile.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None

    objects = CustomUserManager()
