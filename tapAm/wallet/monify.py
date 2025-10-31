import json

import requests
import wireup
from requests import HTTPError
from rest_framework import status
from rest_framework.response import Response
from wireup import service

from .headers import monify_header
from .endpoints import wallet, singleTransfer, authToken, singleOTPValidation, walletBalance
from .tapam import TapAmService


def get_request_key(func):
    try:
        return func()
    except KeyError as ke:
        raise Exception(f"{ke.__str__()} is missing from your request")


@service
class MonifyService:

    def __init__(self):
        container = wireup.create_sync_container(services=[TapAmService])
        self.tapam_service = container.get(TapAmService)

    def post(self, url, client_request, headers=monify_header):
        print('MAKING_CALL:', url, headers, client_request)
        response = requests.post(url, headers=headers,
                                 json=client_request)
        json_response = response.json()
        print('RESPONSE:', url, json_response)
        if not json_response.get('requestSuccessful'):
            msg = json_response.get('responseMessage')
            raise HTTPError(msg if msg else 'An unknown error has occurred. Please try again!')
        return json_response

    def get(self, url, params=None):
        response = requests.get(url, params=params,
                                headers=monify_header)
        json_response = response.json()
        print('RESPONSE:', url, params, json_response)
        if not json_response.get('requestSuccessful'):
            print('json_response001', json_response)
            raise HTTPError(json_response["responseMessage"])
        return json_response

    def create_wallet(self, client_request):
        return self.post(wallet, client_request)

    def make_single_transfer(self, client_request, headers):
        client_request = json.loads(client_request)
        print("validation_client_request", client_request)
        pay_token_request = {
            'request_id': get_request_key(lambda: client_request['reference']),
            'device_id': get_request_key(lambda: client_request['deviceId']),
            'token_id': get_request_key(lambda: client_request['tokenId']),
        }
        pay_token_headers = {
            'X-OFFLINE': get_request_key(lambda: headers['X-OFFLINE']),
            'X-SUB-MID': get_request_key(lambda: headers['X-SUB-MID'])
        }

        validation_result_json = None
        try:
            validation_result = self.tapam_service.validate_token(pay_token_request, pay_token_headers)
            print("validation_result", validation_result)
            validation_result_json = validation_result.json()
            validation_result.raise_for_status()
            validation_data = validation_result_json['data']
            print("validation_result_json", validation_data)
            is_valid = validation_data.get("status") == 'IN_USE' # todo: investigate this later
            print("client_request", client_request)
            if is_valid:
                return self.post(singleTransfer, client_request=client_request, )
        except requests.exceptions.HTTPError as e:
            # {'data': None, 'error': 'Provided payment token is invalid'}
            print("validation_result", validation_result_json)
            raise TypeError(validation_result_json['error'])

    def get_wallets_by_email(self, customer_email) -> Response:  # ?pageSize=10&pageNo=0
        response = self.get(wallet, params={
            'customerEmail': customer_email
        })
        print("response_json", response)
        return response

    def validate_otp(self, client_request):
        return self.post(singleOTPValidation, client_request=client_request)

    def get_wallet_balance(self, acct_number):
        return self.get(walletBalance, params={
            'accountNumber': acct_number,
           # 'accountNumber':
        })

    def generate_token(self):
        result = self.post(authToken, client_request={})
        return result["responseBody"]['accessToken']

    def confirm_tapam_pay_token(self, request_id: str, status: str):
        request = {
            'request_id': request_id,
            'status': status
        }
        pay_token_confirmation = self.tapam_service.confirm_pay_token(request)
        pay_token_confirmation_json = pay_token_confirmation.json()
        pay_token_confirmation.raise_for_status()
        return pay_token_confirmation_json

# single-transfer = {
#     "amount": 200,
#     "reference":"referen00ce---1290034",
#     "narration":"911 Transaction",
#     "destinationBankCode": "057",
#     "destinationAccountNumber": "2085886393",
#     "currency": "NGN",
#     "sourceAccountNumber": "3934178936"
# }
