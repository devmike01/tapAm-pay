import requests
from wireup import service


payTokenValidationApi = 'https://b18e10dc602e.ngrok-free.app/offline/use'
confirmTransactionApi = 'https://b18e10dc602e.ngrok-free.app/offline/update-state'

tapAmSubMid = 'X-SUB-MID'
tapAmOfflineToken = 'X-OFFLINE'


@service
class TapAmService:

    def __init__(self):
        self.headers = {
            'X-API-KEY': 'tapam_1trbmom8dfe3g9zrnop4vfvg8u5tf1cyqlc7o63k5d18fot4vr',
            'X-API-OWNER': 'dev0*',
            'Content-Type': 'application/json'
        }

    def validate_token(self, client_request, headers):
        return requests.post(payTokenValidationApi,
                             headers={**headers, **self.headers},
                             json=client_request)

    def confirm_pay_token(self, client_request):
        return requests.post(confirmTransactionApi,
                             headers=self.headers,
                             json=client_request)
