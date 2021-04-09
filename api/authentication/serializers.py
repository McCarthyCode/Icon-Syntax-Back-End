import re
import jwt

from django.conf import settings
from django.contrib.auth import authenticate, password_validation as validators
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from rest_framework import serializers, exceptions
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .exceptions import ConflictError
from .models import User
from .utils import Util


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializes username, email, and password and creates users for use in registration.
    """
    class Meta():
        model = User
        fields = ['username', 'email', 'password']

    username = serializers.CharField(max_length=64)
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(
        min_length=8, max_length=64, write_only=True)

    def validate(self, data):
        """
        Check password against built-in validators.
        """
        # Check password
        if self.instance:
            # PUT, PATCH
            user = self.instance
            for key, value in data:
                user[key] = value
        else:
            # POST
            user = User(**data)

        validators.validate_password(password=data.get('password'), user=user)

        # Check for existing username and password
        username_exists = User.objects.filter(
            username=data.get('username')).exists()
        email_exists = User.objects.filter(email=data.get('email')).exists()

        if username_exists or email_exists:
            username_dict = {
                'username': 'A user with this username already exists.'
            } if username_exists else {}
            email_dict = {
                'email': 'A user with this email address already exists.'
            } if email_exists else {}

            raise ConflictError(dict(username_dict, **email_dict))

        return super().validate(data)

    def create(self, validated_data):
        """
        Create the User object by passing validated_data to create_user method in manager.
        """
        return User.objects.create_user(**validated_data)


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


class RegisterVerifySerializer(AuthAbstractSerializer):
    """
    Serializes username, email, and tokens from an access token for logging in after verifying an email address.
    """
    class Meta():
        model = User
        fields = ['access', 'username', 'email', 'tokens']

    def validate(self, data):
        """
        Retrieve the user, mark their email address as verified, and return serialized data on success. On failure, the _get_user() method called by validate() will raise one of four possible exceptions, as outlined in the _get_user() docstring.
        """
        user = self._get_user(data)
        user.is_verified = True
        user.save()

        return data


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
