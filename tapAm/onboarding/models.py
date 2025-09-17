from django.db import models
from django.contrib.auth.models import AbstractBaseUser, AbstractUser, PermissionsMixin
from django.utils import timezone

from .acct_statuses import *
from .model_manager import CustomUserManager


# Create your models here.
class UserProfile(AbstractUser, PermissionsMixin):
    email = models.EmailField(unique=True, default='', null=False)
    # USERNAME_FIELD = 'email'
    username = models.CharField(max_length=100, default='', null=False, unique=True)
    cust_id = models.CharField(max_length=200, default='', null=False)
    cust_phone = models.CharField(max_length=15, default='')
    image_url = models.CharField(max_length=200, default='', null=True)
    uid = models.CharField(max_length=100, default='', null=False)  # public user id depre
    ACCT_STATUS = (
        (VERIFIED, "Verified"),
        (SUSPENDED, "suspended"),
        (UNVERIFIED, "Unverified")
    )
    account_status = models.CharField(max_length=15, default=UNVERIFIED, choices=ACCT_STATUS)
    objects = CustomUserManager()


class EmailOtpValidation(models.Model):
    otp = models.CharField(max_length=7, default='', null=False, unique=True)
    created_at = models.DateTimeField(auto_now=True)
    expired_at = models.DateTimeField(default=timezone.now, null=False)
    cust_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, default=1)
