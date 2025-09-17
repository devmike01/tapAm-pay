from django.contrib.auth.password_validation import validate_password
from onboarding.models import UserProfile
from onboarding.serializers.token_serializer import AppTokenObtainPairSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from core.serializer import required


class RegisterSerializer(serializers.ModelSerializer, AppTokenObtainPairSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=UserProfile.objects.all())]
    )

    password = serializers.CharField(write_only=True, required=True,
                                     validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = UserProfile
        fields = ('password', 'password2', 'first_name',
                  'last_name', 'id', 'cust_phone', 'last_name',
                  'image_url', 'email')
        extra_kwargs = {
            'first_name': required,
            'cust_phone': required,
            'last_name': required,
            'email': required
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs


class EditProfileSerializer(serializers.ModelSerializer):

    def create(self, validated_data: dict):
        userprofile = UserProfile.objects.filter(cust_id=validated_data['cust_id'])[0]
        first_name = validated_data.get('first_name')
        lastname = validated_data.get('lastname')
        cust_phone = validated_data.get('cust_phone')
        email = validated_data.get('email')
        profession = validated_data.get('profession')
        print('request_data:: ', profession)

        userprofile.profession = profession if profession else userprofile.profession
        userprofile.first_name = first_name if first_name else userprofile.first_name
        userprofile.lastname = lastname if lastname else userprofile.lastname
        userprofile.cust_phone = cust_phone if cust_phone else userprofile.cust_phone
        userprofile.email = email if email else userprofile.email
        userprofile.save()

        response = {
            'first_name': userprofile.first_name,
            'lastname': userprofile.lastname,
            'cust_phone': userprofile.cust_phone,
            'email': userprofile.email,
            'profession': userprofile.profession.profession_name
        }
        # response['profession'] =

        return response

    class Meta:
        model = UserProfile
        fields = ('first_name',
                  'lastname', 'cust_phone', 'lastname',
                  'image_url', 'email', 'profession')
        extra_kwargs = {
            'cust_id': {'required': True},
            'lastname': {'required': False},
        }
