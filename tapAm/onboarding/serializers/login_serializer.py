from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from django.middleware.csrf import get_token
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .token_serializer import AppTokenObtainPairSerializer

user = get_user_model()


class LoginSerializers(serializers.ModelSerializer):
    email = serializers.CharField(max_length=50)

    password = serializers.CharField(write_only=True, required=True,
                                     validators=[validate_password])

    class Meta:
        model = user
        fields = ('password', 'email')
        extra_kwargs = {
            'email': {'required': True},
            'password': {'required': True}
        }

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        # Django built-in authentication function
        print('login_validation: {} {}'.format(email, password))
        user = authenticate(username=email, password=password)
        if user:
            if user.is_active:
                # update_last_login(None, user)
                token, created = Token.objects.get_or_create(user=user)
                print('login_validation_user: {}'.format(token))
                data['token'] = AppTokenObtainPairSerializer.get_token(user)
                data['user_id'] = user.id
                return data
            else:
                raise serializers.ValidationError('User is not active', code='authorization')
        else:
            msg = 'Someone tried to login and failed'
            serializers.ValidationError(msg, code='authorization')
        return data

    @classmethod
    def create(cls, validated_data):
        update_last_login(None, user)
        token, created = Token.objects.get_or_create(user=user)

        return user
