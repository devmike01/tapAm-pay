from rest_framework import serializers

from onboarding.models import MentorPayment
from core.json_serializer import extract_fields

from onboarding.models import UserProfile


class MentorPaymentSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user_profile = UserProfile.objects.filter(cust_id=validated_data['cust_id'])[0]
        print("MANGE TANGO {}".format(user_profile.mentor_payment))
        if user_profile.mentor_payment:
            user_profile.mentor_payment.minor_charges = validated_data['minor_charges']
            user_profile.mentor_payment.currency = validated_data['currency']
            user_profile.mentor_payment.save()
        else:
            user_profile.mentor_payment = MentorPayment.objects.create(
                minor_charges=validated_data['minor_charges'],
                currency=validated_data['currency'],
                cust_id=validated_data['cust_id'])
        user_profile.save()
        return extract_fields(user_profile.mentor_payment)

    class Meta:
        model = MentorPayment
        fields = ['minor_charges', 'currency', 'cust_id']
