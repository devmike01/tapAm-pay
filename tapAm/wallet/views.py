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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get(self, request):
        try:
            self.api_result.success(self.monify.get_wallets_by_email(
                customer_email=str(request.GET.get('email'))
            ))
            return self.api_result.to_response()
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
            print('data_request:', str(json.dumps(request.data)))
            transfer_otp_result = self.monify.validate_otp(
                client_request=json.dumps(request.data)
            )
            otp_validation_state: str = transfer_otp_result['responseMessage']
            if otp_validation_state.lower() != "success":
                raise TypeError(otp_validation_state)
            response_body = transfer_otp_result['responseBody']
            tapam_headers = {
                tapAmSubMid: request.headers[tapAmSubMid],
                tapAmOfflineToken: request.headers[tapAmOfflineToken]
            }
            result = self.monify.confirm_tapam_pay_token(headers=tapam_headers,
                                                         request_id=response_body['reference'],
                                                         status="success")
            if result['data'] is None:
                raise HTTPError(result['error'])
            return self.api_result.success(response_body).to_response()
        except Exception as ex:
            self.api_result.failed(str(ex))
            return self.api_result.to_response()
