import jwt

from tapAm import settings


class JwtChecks:

    def valid_token_email(self, request, email) -> bool:
        token = request.META.get('HTTP_AUTHORIZATION')
        tokenn = token.split(" ")[1]
        token_dict = jwt.decode(tokenn, settings.SECRET_KEY, algorithms=["HS256"])
        return token_dict['email'] == email
