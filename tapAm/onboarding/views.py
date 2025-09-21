import base64
import json
import uuid

from core.email_sender import send_otp_email
from core.json_serializer import extract_fields, extract_error
from core.jwt_decoded import JwtChecks
from core.otp_generator import get_otp
from django.contrib.auth import logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import generics, status, permissions
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt import authentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .acct_statuses import VERIFIED, UNVERIFIED
from .models import UserProfile, EmailOtpValidation
from .serializers.register_serializer import RegisterSerializer, EditProfileSerializer
from .serializers.token_serializer import AppTokenObtainPairSerializer
from core.sanitizers import normalize


class LoginTokenView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = AppTokenObtainPairSerializer

    def post(self, request: Request, *args, **kwargs) -> Response:
        # request.data.pop('email')
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            print("user__user02", serializer.validated_data)
            user = authenticate(username=request.data['username'],
                                password=request.data['password'])
            print("user__user", user.email, user.first_name, user)
            if user.account_status == UNVERIFIED:
                send_otp_email(user.email, user.first_name, user)

        except Exception as e:
            return Response({
                "message": f"{e}",
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "data": {
                    "access_token": serializer.validated_data,
                    "first_name": user.first_name,
                    "lastname": user.last_name,
                    "cust_id": user.cust_id,
                    "email": user.email,
                    "cust_phone": user.cust_phone,
                    "pub_uid": user.uid,
                    'image_url': user.image_url,
                    "acct_status": user.account_status
                }
            },
            status=status.HTTP_200_OK)


class OnboardingOtp(generics.CreateAPIView, APIView):
    # serializer_class = OtpValidatorSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.jwtChecks = JwtChecks()

    def post(self, request, *args, **kwargs):
        try:
            user = UserProfile.objects.get(cust_id=request.data['cust_id'])
            if not self.jwtChecks.valid_token_email(request, user.email):
                raise Exception("Email don't match token")
            otp = EmailOtpValidation.objects.filter(otp=request.data['otp']).filter(
                cust_profile=user
            )

            if otp.exists():
                otp_data = otp[0]
                if otp_data.expired_at < timezone.now():
                    otp.delete()
                otp.delete()  # OTP was validated. We no longer need it
                user.account_status = VERIFIED
                user.save()
                return Response({"data": extract_fields(otp_data)})
            return Response({"message": "Invalid otp"},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({"message": "Unable to validate the provided OTP. Please, try again."},
                            status=status.HTTP_403_FORBIDDEN)

    # Send OTP
    def get(self, request, cust_id: str):
        try:
            user = UserProfile.objects.filter(cust_id=cust_id)[0]
            otp = EmailOtpValidation.objects.filter(cust_profile=user.id)
            if otp.exists():
                otp_data = otp[0]
                if otp_data.expired_at > timezone.now():
                    return Response({"message": f"Wait for "
                                                f"{round((otp_data.expired_at - timezone.now()).total_seconds())}"},
                                    status=status.HTTP_403_FORBIDDEN)
                else:
                    # Delete column data if an otp already exists
                    otp.delete()

            valid_email = self.jwtChecks.valid_token_email(request, user.email)
            if valid_email:
                send_otp_email(user.email, user.first_name, user)
                email_segment = user.email.split("@")
                email_user = email_segment[0]
                visible_start = len(email_user) // 3
                mask_len = len(email_user) - visible_start

                return Response({
                    'data': f'Otp was sent to your email {email_user[0:visible_start]}{"*" * mask_len}@{email_segment[1]}'
                })
            else:
                return Response({"message": "Email and token don't match"},
                                status=status.HTTP_403_FORBIDDEN)
        except Exception as ex:
            print("get_get", f"{ex}")
            return Response({"message": extract_error(ex)},
                            status=status.HTTP_400_BAD_REQUEST)


class RegisterView(generics.CreateAPIView):
    queryset = UserProfile.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create_user(self, validated_data, baseurl: str):
        sample_string = str(uuid.uuid1())
        sample_string_bytes = sample_string.encode("ascii")
        base64_bytes = base64.b64encode(sample_string_bytes)
        base64_uuid = base64_bytes.decode("ascii")
        validated_data['cust_id'] = base64_uuid

        # country = CountryData.objects.filter(
        #     country_code=validated_data['country_code']
        # )
        # mentor_payment = MentorPayment.objects.create(
        #     minor_charges=1500,
        #     cust_id=validated_data.get('cust_id'))

        user = UserProfile.objects.create(
            username=normalize(validated_data.get('email')),
            email=normalize(validated_data.get('email')),
            cust_id=normalize(validated_data.get('cust_id')),
            first_name=normalize(validated_data.get('first_name')),
            last_name=normalize(validated_data.get('last_name')),
            cust_phone=normalize(validated_data.get('cust_phone')),
            image_url=normalize(validated_data.get('image_url')),
            password=normalize(validated_data.get('password')),
            # user_country=country[0],
            uid=get_otp()
        )

        user.set_password(validated_data['password'])
        user.save()
        return user

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            baseurl = request.build_absolute_uri()
            serializer.is_valid(raise_exception=True)
            user = self.create_user(request.data, baseurl)
            token_class = AppTokenObtainPairSerializer

            try:
                send_otp_email(user.email, user.first_name, user)
            except Exception as e:
                print('send_otp_email', e)

            return Response(
                {
                    "data": {
                        "first_name": user.first_name,
                        "lastname": user.last_name,
                        "cust_id": user.cust_id,
                        "email": user.email,
                        "pub_uid": user.uid,
                        "acct_status": user.account_status,
                        "image_url": user.image_url
                    }
                }, status=status.HTTP_200_OK)
        except Exception as e:
            error_dict = dict(e.__dict__.get('detail'))
            detail = list(error_dict.values())[-1]
            field = list(error_dict.keys())[-1]
            if len(detail) > 0:
                return Response({"message": f"{field}: {detail[0].title()}".lower()},
                                status=status.HTTP_401_UNAUTHORIZED)
            return Response({"message": "An unknown error has occurred."}, status=status.HTTP_401_UNAUTHORIZED)


@login_required
def special(_):
    return HttpResponse("You're logged in. Nice")


class UserLogout(APIView):
    authentication_classes = [authentication.JWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        try:
            logout(request)
            return Response(
                {
                    "data": {
                        "redirect": "/"
                    }
                }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": "An unknown error has occurred."}, status=status.HTTP_401_UNAUTHORIZED)


class EditProfileApi(CreateAPIView, APIView):
    serializer_class = EditProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            request_data: dict = {}

            for field in request.data:
                if request.data.get(field):
                    request_data[field] = request.data[field]

            serializer = self.get_serializer(data=request_data)
            serializer.is_valid(raise_exception=True)
            serializer.save(cust_id=request.data['cust_id'])
            response_data = serializer.validated_data

            return Response({
                'data': response_data
            })
        except Exception as err:
            return Response(
                {
                    "message": extract_error(err)
                }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        pass
