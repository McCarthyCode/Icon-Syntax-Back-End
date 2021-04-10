from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

from rest_framework import serializers, exceptions
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from ..models import User

from .abstract import AccessTokenAbstractSerializer


class LoginSerializer(serializers.ModelSerializer):
    """
    Serializes username, email, password, and tokens to allow for logging in.
    """
    class Meta():
        model = User
        fields = ['username', 'email', 'password', 'tokens']

    username = serializers.CharField(max_length=64)
    email = serializers.CharField(max_length=254, read_only=True)
    password = serializers.CharField(
        min_length=8, max_length=64, write_only=True)
    tokens = serializers.SerializerMethodField(read_only=True)

    def get_tokens(self, obj):
        """
        Return output of object's tokens method for use in the tokens serializer field.
        """
        return User.objects.get(username=obj['username']).tokens()

    def validate(self, data):
        """
        Authenticate the user and return serialized data on success. On failure, raise an AuthenticationFailed exception with an appropriate error message.
        """
        username = data.get('username', '')
        password = data.get('password', '')

        authenticated_user = authenticate(username=username, password=password)
        if not authenticated_user:
            try:
                unauthenticated_user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise exceptions.AuthenticationFailed(
                    'The credentials used to login were invalid.')

            if not unauthenticated_user.is_active:
                raise exceptions.AuthenticationFailed(
                    'Your account has been temporarily disabled. Please contact the site administrator at webmaster@iconopedia.org.'
                )

            raise exceptions.AuthenticationFailed(
                'The credentials used to login were invalid.')
        else:
            if not authenticated_user.is_verified:
                raise exceptions.AuthenticationFailed(
                    'Your account has not been verified. Please check your email for a confirmation link.'
                )

        return {
            'username': authenticated_user.username,
            'email': authenticated_user.email,
            'tokens': authenticated_user.tokens(),
        }


class LogoutSerializer(AccessTokenAbstractSerializer):
    """
    Serializes access token to allow for logging out.
    """
    def validate(self, data):
        """
        Blacklist the refresh token. On failure, raise ValidationError.
        """
        refresh = self._get_user(data).tokens()['refresh']

        try:
            RefreshToken(refresh).blacklist()
        except TokenError:
            self.fail('bad_token')

        return data
