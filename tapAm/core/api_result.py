import json

from rest_framework import status
from rest_framework.response import Response
from wireup import service


@service
class ApiResult:

    def __init__(self):
        self.result = {}

    def success(self, data):
        self.result['success'] = data
        return self

    def failed(self, msg):
        self.result['error'] = msg

    def get(self) -> dict:
        return self.result

    def to_response(self, success_status_code: int = status.HTTP_200_OK,
                    error_code=status.HTTP_400_BAD_REQUEST):
        if self.result.get('success'):
            return Response(data=self.result, status=success_status_code)
        elif self.result.get('error'):
            return Response(data=self.result, status=error_code)
        else:
            raise Exception("Invalid api state")
