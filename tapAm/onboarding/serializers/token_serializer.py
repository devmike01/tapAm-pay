from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.authtoken.models import Token


class AppTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        cls.user = user
        return token

    # def validate(self, attrs: dict):
    #     data = super().validate(attrs)
    #     data.update({
    #         "user_id": self.user,
    #         "username": self.user.email
    #     })
    #
    #     return data
