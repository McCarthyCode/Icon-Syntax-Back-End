from jwt.exceptions import DecodeError, ExpiredSignatureError

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, ErrorDetail

from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .login_logout import LoginSerializer


class RefreshSerializer(LoginSerializer):
    """
    Serializer that takes in login credentials plus a refresh token to obtain a token pair with moderately strict security.
    """
    refresh = serializers.CharField(max_length=4096)

    def validate_refresh(self, value):
        """
        Field-level validation method for checking a refresh token. The method attempts to blacklist the token, returning the original value on success or raising AuthenticationFailed on failure.
        """
        try:
            token = RefreshToken(value)
            token.blacklist()
        except (DecodeError, ExpiredSignatureError, TokenError) as exc:
            msg = str(exc)
            if msg[-1] not in '.?!':
                msg += '.'
            raise AuthenticationFailed(ErrorDetail(msg, 'invalid'))

        return value
