import json
import os
import traceback
from os.path import join, dirname

import requests
import wireup
from requests import HTTPError, Request
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from dotenv import load_dotenv

from core.view_bases import AuthenticatedAPIView, AuthenticatedCreateApiView
from rest_framework.response import Response
from wireup import service

from .endpoints import wallet
from .monify import MonifyService
from .monify_request_adaptor import monify_create_wallet
from rest_framework import status

from core.api_result import ApiResult

from .tapam import TapAmService, tapAmSubMid, tapAmOfflineToken

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


# Create your views here.
class CreateWallet(AuthenticatedCreateApiView):

    def __init__(self):
        container = wireup.create_sync_container(services=[MonifyService, ApiResult])
        self.monify = container.get(MonifyService)
        self.api_result = container.get(ApiResult)

    def post(self, request, *args, **kwargs):

        client_response = {}

        try:
            client_response['data'] = self.monify \
                .create_wallet(monify_create_wallet(request.data))
            return Response(data=client_response, status=status.HTTP_201_CREATED)
        except HTTPError as e:
            print(e)
            client_response['error'] = str(e)
            return Response(data=client_response, status=status.HTTP_400_BAD_REQUEST)


class GetWallets(AuthenticatedAPIView):

    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get(self, request):
        try:
            print("request.GET", request.GET.get('email'))
            return self.api_result.success(self.monify.get_wallets_by_email(
                customer_email=str(request.GET.get('email'))
            )).to_response()
        except HTTPError as e:
            print(e)
            self.api_result.failed('Failed to fetch your wallet. Please, try again.')
            return self.api_result.to_response()
        except TypeError as te:
            self.api_result.failed('Invalid request')
            return self.api_result.to_response()


class SingleTransfer(generics.CreateAPIView):
    authentication_classes = []  # No authentication required
    permission_classes = (AllowAny,)

    def __init__(self, **kwargs):
        container = wireup.create_sync_container(services=[ApiResult, MonifyService])
        self.monify = container.get(MonifyService)
        self.api_result = container.get(ApiResult)
        super().__init__(**kwargs)

    def post(self, request, *args, **kwargs):
        try:
            headers = request.headers
            single_transfer = self.monify.make_single_transfer(
                client_request=json.dumps(request.data),
                headers=headers
            )
            return self.api_result.success(single_transfer["responseBody"]).to_response()
        except Exception as ex:
            print(f'error001 -> {ex}', ex)
            traceback.print_exc()
            return self.api_result.error_response(str(ex))
        # return self.api_result.to_response()


class TransferOTPValidation(generics.CreateAPIView):
    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        container = wireup.create_sync_container(services=[ApiResult, MonifyService])
        self.api_result = container.get(ApiResult)
        self.monify = container.get(MonifyService)
        super().__init__(**kwargs)

    def post(self, request, *args, **kwargs):
        try:
            transfer_otp_result = self.monify.validate_otp(
                client_request=request.data
            )
            print('data_request0001:', str(transfer_otp_result))
            otp_validation_state: str = transfer_otp_result['responseMessage']
            if otp_validation_state.lower() != "success":
                raise TypeError(otp_validation_state)
            response_body = transfer_otp_result['responseBody']

            result_json = self.monify.confirm_tapam_pay_token(request_id=response_body['reference'],
                                                              status="success")

            return self.api_result.success({**response_body, **result_json}).to_response()
        except Exception as ex:
            traceback.print_exc()
            self.api_result.failed(str(ex))
            return self.api_result.to_response()


class WalletBalance(generics.RetrieveAPIView):

    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        container = wireup.create_sync_container(services=[ApiResult, MonifyService])
        self.api_result = container.get(ApiResult)
        self.monify = container.get(MonifyService)
        super().__init__(**kwargs)

    def get(self, request, acct_number):
        # get_wallet_balance
        try:
            print('acct_number', acct_number)
            # /wallet/{ref}
            bal_json = self.monify.get_wallet_balance(acct_number)
            return self.api_result.success(bal_json).to_response()
        except KeyError as ke:
            traceback.print_exc()
            self.api_result.failed(f"invalid wallet path({ke})")
            return self.api_result.to_response()
        except Exception as ex:
            traceback.print_exc()
            self.api_result.failed(str(ex))
            return self.api_result.to_response()

