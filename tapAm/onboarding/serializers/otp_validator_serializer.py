from rest_framework import serializers

from onboarding.models import EmailOtpValidation
from core.validators import required


class OtpValidatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailOtpValidation
        fields = ('otp', 'created_at', 'expired_at',
                  'cust_id')
        extra_kwargs = {
            'otp': required,
            'cust_id': required,
        }

    def validate(self, attrs):
        otp = attrs['otp']
        if len(otp) >= 6:
            raise serializers.ValidationError({"otp": "Wrong OTP length"})
        return attrs
