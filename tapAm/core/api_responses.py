from rest_framework import status
from rest_framework.response import Response

content_type = 'json/application'


class OKResponse(Response):
    def __init__(self, data):
        super().__init__(status=status.HTTP_200_OK, data=data, content_type=content_type)


class OkCreatedResponse(Response):
    def __init__(self, data):
        super().__init__(status=status.HTTP_201_CREATED, data=data, content_type=content_type)


class BadRequestResponse(Response):
    def __init__(self, data):
        super().__init__(status=status.HTTP_400_BAD_REQUEST, data=data, content_type=content_type)
