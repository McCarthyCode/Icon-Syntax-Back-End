import re

from django.conf import settings
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

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

    username = serializers.CharField(max_length=64, required=False)
    email = serializers.EmailField(max_length=254, required=False)
    password = serializers.CharField(
        min_length=8,
        max_length=64,
        write_only=True,
        style={'input_type': 'password'})

    default_error_messages = {
        'id_required':
        _('A username or email is required.'),
        'invalid':
        _('The credentials used to login were invalid.'),
        'disabled':
        _(
            'Your account has been temporarily disabled. Please contact the site administrator at webmaster@iconopedia.org.'
        ),
        'unverified':
        _(
            'Your account has not been verified. Please check your email for a confirmation link.'
        ),
    }

    def validate(self, data):
        """
        Authenticate the user and return serialized data on success. On failure, raise an AuthenticationFailed exception with an appropriate error message.
        """
        # Retrieve data fields, defaulting to None
        username = data.get('username', None)
        email = data.get('email', None)
        password = data.get('password', None)

        # Authenticate user based on username or email, and password.
        # On failure, raise an appropriate exception (either ValidationError or
        # AuthenticationFailed).
        if username:
            authenticated_user = authenticate(
                username=username, password=password)
        elif email:
            try:
                username = User.objects.get(email=email).username
            except User.DoesNotExist:
                raise exceptions.AuthenticationFailed(
                    self.error_messages['invalid'], 'invalid')

            authenticated_user = authenticate(
                username=username, password=password)
        else:
            self.fail('id_required')

        # If authentication failed but input is valid, find out the cause and
        # report the issue with an AuthenticationFailed exception.
        if not authenticated_user:
            try:
                unauthenticated_user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise exceptions.AuthenticationFailed(
                    self.error_messages['invalid'], 'invalid')

            if not unauthenticated_user.is_active:
                raise exceptions.AuthenticationFailed(
                    self.error_messages['disabled'], 'disabled')

            raise exceptions.AuthenticationFailed(
                self.error_messages['invalid'], 'invalid')
        elif not authenticated_user.is_verified:
            raise exceptions.AuthenticationFailed(
                self.error_messages['unverified'], 'unverified')

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
            self.fail('invalid')

        return data
