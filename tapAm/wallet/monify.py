import requests
from requests import Response, HTTPError
from wireup import service

from .headers import monify_header
from .endpoints import wallet, singleTransfer, authToken


@service
class MonifyService:

    def __init__(self):
        pass

    def post(self, url, client_request, headers=monify_header):
        print('monify_header', headers)
        response = requests.post(url, headers=headers,
                                 data=client_request)
        json_response = response.json()
        if not json_response.get('requestSuccessful'):
            msg = json_response.get('responseMessage')
            raise HTTPError(msg if msg else 'An unknown error has occurred. Please try again!')
        return json_response

    def get(self, url, params=None):
        response = requests.get(url, params=params,
                                headers=monify_header)
        json_response = response.json()
        if not json_response.get('requestSuccessful'):
            raise HTTPError(json_response["responseMessage"])
        return json_response

    def create_wallet(self, client_request):
        return self.post(wallet, client_request)

    def make_single_transfer(self, client_request):
        return self.post(singleTransfer, client_request,)

    def get_wallets_by_email(self, customer_email) -> Response:  # ?pageSize=10&pageNo=0
        response = self.get(wallet, params={
            'customerEmail': customer_email
        })
        return response



# single-transfer = {
#     "amount": 200,
#     "reference":"referen00ce---1290034",
#     "narration":"911 Transaction",
#     "destinationBankCode": "057",
#     "destinationAccountNumber": "2085886393",
#     "currency": "NGN",
#     "sourceAccountNumber": "3934178936"
# }
