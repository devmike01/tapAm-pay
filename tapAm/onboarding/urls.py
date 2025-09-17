from django.urls import path, include

from . import views
from .views import LoginTokenView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("login", LoginTokenView.as_view(), name="token"),
    path('register', views.RegisterView.as_view(), name='user_register'),
    path('login/refresh', TokenRefreshView.as_view(), name='refresh_token'),
    path('logout', views.UserLogout.as_view(), name='logout'),
    path('otp/<str:cust_id>', views.OnboardingOtp.as_view(), name='onboarding_otp'),
    path('validate-otp', views.OnboardingOtp.as_view(), name='onboarding_otp'),
    path('edit-profile', views.EditProfileApi.as_view(), name='edit-profile')
]
