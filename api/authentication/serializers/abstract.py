import re
import jwt

from django.conf import settings
from django.core.exceptions import ValidationError

from rest_framework import serializers

from ..models import User


class AccessTokenAbstractSerializer(serializers.Serializer):
    """
    Abstract base class for any serializer that takes in an access token and obtains the appropriate user.
    """
    access = serializers.CharField(max_length=4096, write_only=True)
    user = None

    default_error_messages = {
        'bad_token': 'Access token is expired or invalid.'
    }

    def _get_user(self, obj):
        """
        Retrieve the user instance defined by the given access token. On failure, one of four possible exceptions will be raised: jwt.exceptions.DecodeError, jwt.exceptions.ExpiredSignatureError, rest_framework.exceptions.ValidationError, or api.authentication.models.User.DoesNotExist
        """
        if not self.user:
            payload = jwt.decode(
                obj['access'],
                settings.SECRET_KEY,
                algorithms=['HS256'],
            )

            self.user = User.objects.get(id=payload['user_id'])

        return self.user

    def validate_access(self, value):
        """
        Validate the access token, checking against TOKEN_REGEX, and logout its associated user on success. On failure, raise a ValidationError exception with an appropriate error message.
        """
        try:
            assert re.match(settings.TOKEN_REGEX, value)
        except AssertionError:
            self.fail('bad_token')

        return value

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
