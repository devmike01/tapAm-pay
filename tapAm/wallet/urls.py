from django.urls import path, include

from . import views
from .views import CreateWallet, GetWallets, SingleTransfer
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("create", CreateWallet.as_view(), name="create"),
    path("all", GetWallets.as_view(), name="wallets"),
    path("transfer", SingleTransfer.as_view(), name="single-transfer")
]
