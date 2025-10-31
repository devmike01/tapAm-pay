from django.urls import path, include

from .views import CreateWallet, GetWallets, SingleTransfer, TransferOTPValidation, WalletBalance
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("create", CreateWallet.as_view(), name="create"),
    path("all", GetWallets.as_view(), name="wallets"),
    path("transfer", SingleTransfer.as_view(), name="single-transfer"),
    path("transfer/validate-otp", TransferOTPValidation.as_view(), name="validate-transfer-otp"),
    path("<str:acct_number>", WalletBalance.as_view(), name="get-wallet-balance")
]
