import json
import os
from os.path import join, dirname

import requests
import wireup
from requests import HTTPError, Request
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from dotenv import load_dotenv

from core.view_bases import AuthenticatedAPIView, AuthenticatedCreateApiView
from rest_framework.response import Response
from wireup import service

from .endpoints import wallet
from .monify import MonifyService
from .monify_request_adaptor import monify_create_wallet
from rest_framework import status

from core.api_result import ApiResult

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


# Create your views here.
class CreateWallet(AuthenticatedCreateApiView):

    def __init__(self, monify: MonifyService, api_result: ApiResult):
        self.monify = monify
        self.api_result = api_result

    def post(self, request, *args, **kwargs):

        client_response = {}

        try:
            client_response['data'] = self.monify\
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


class SingleTransfer(AuthenticatedCreateApiView):

    def post(self, request, *args, **kwargs):
        try:
            print('data_request:', request.data)
            # Authorizationbearer
            single_transfer = self.monify.make_single_transfer(
                monify_create_wallet(request.data))
            self.api_result.success(single_transfer)
            return self.api_result.to_response()
        except HTTPError as ex:
            self.api_result.failed(str(ex))
            return self.api_result.to_response()
