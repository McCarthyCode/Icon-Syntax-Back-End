import re
import jwt

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from jwt.exceptions import DecodeError, ExpiredSignatureError

from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from ..models import User


class AccessTokenAbstractSerializer(serializers.Serializer):
    """
    Abstract base class for any serializer that takes in an access token and obtains the appropriate user.
    """
    access = serializers.CharField(max_length=4096, write_only=True)
    user = None

    default_error_messages = {
        'invalid': _('The token provided is invalid.'),
        'expired': _('The token provided has expired.'),
        'user_gone': _('The user associated with this token no longer exists.'),
    }

    def _get_user(self, obj):
        """
        Retrieve the user instance defined by the given access token. On failure, ValidationError or GoneError is raised.
        """
        if not self.user:
            try:
                payload = jwt.decode(
                    obj['access'],
                    settings.SECRET_KEY,
                    algorithms=['HS256'],
                )
            except DecodeError:
                raise ValidationError(
                    {'access': self.error_messages['invalid']}, 'invalid')
            except ExpiredSignatureError:
                raise GoneError(
                    {'access': self.error_messages['expired']}, 'expired')

            try:
                self.user = User.objects.get(id=payload['user_id'])
            except User.NotFound:
                raise ValidationError(
                    self.error_messages['user_gone'],
                    'user_gone',
                    status_code=status.HTTP_410_GONE)

        return self.user

    def validate_access(self, value):
        """
        Validate the access token, checking against TOKEN_REGEX, and logout its associated user on success. On failure, raise a ValidationError exception with an appropriate error message.
        """
        auth = value.split(' ')

        try:
            assert len(auth) == 2
            assert auth[0] == 'Bearer'
            assert re.match(settings.TOKEN_REGEX, auth[1])
        except AssertionError:
            self.error_messages['invalid']

        return auth[1]

    def create(self, obj):
        return obj


class AuthAbstractSerializer(AccessTokenAbstractSerializer):
    """
    Abstract base class for any serializer that takes in an access token and outputs the username, email address, and tokens for the appropriate user.
    """
    username = serializers.SerializerMethodField(read_only=True)
    email = serializers.SerializerMethodField(read_only=True)
    tokens = serializers.SerializerMethodField(read_only=True)

    def get_username(self, obj):
        """
        Return user's username based on value of token.
        """
        return self._get_user(obj).username

    def get_email(self, obj):
        """
        Return user's email based on value of token.
        """
        return self._get_user(obj).email

    def get_tokens(self, obj):
        """
        Return output of User instance's tokens() method for use in the tokens serializer field.
        """
        return self._get_user(obj).tokens()
