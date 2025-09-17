import wireup
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.api_result import ApiResult
from wallet.monify import MonifyService


class AuthenticatedCreateApiView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        container = wireup.create_sync_container(services=[MonifyService, ApiResult])
        self.monify = container.get(MonifyService)
        self.api_result = container.get(ApiResult)
        super().__init__(**kwargs)


class AuthenticatedAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        container = wireup.create_sync_container(services=[MonifyService, ApiResult])
        self.monify = container.get(MonifyService)
        self.api_result = container.get(ApiResult)
        super().__init__(**kwargs)
