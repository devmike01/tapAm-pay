import requests
from django.test import TestCase

# Create your tests here.


def get(url, params=None):
    monify_headers = {
        "Authorization": "Basic TUtfVEVTVF8wOENRN0xVUVVLOkpKRkRNOU1QUEpSRUNBTUU2S1cwODhFOFU5VlE4MEhG",
        # If authentication is required
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    response = requests.get("https://sandbox.monnify.com/api/v1/disbursements/wallet?customerEmail=test@gmail.com",
                            headers=monify_headers)
    response.raise_for_status()
    return response.json()


print(get(""))
