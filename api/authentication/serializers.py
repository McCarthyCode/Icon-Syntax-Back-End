import django.contrib.auth.password_validation as validators

from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from rest_framework import serializers, exceptions

from .models import User
from .exceptions import ConflictError


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


class VerifySerializer(serializers.ModelSerializer):
    """
    Serializes username, email, and tokens for logging in after verifying an email address.
    """
    class Meta():
        model = User
        fields = ['username', 'email', 'tokens']

    username = serializers.CharField(max_length=64)
    email = serializers.SerializerMethodField(read_only=True)
    tokens = serializers.SerializerMethodField(read_only=True)

    def get_tokens(self, obj):
        """
        Return output of object's tokens method for use in the tokens serializer field.
        """
        return User.objects.get(username=obj['username']).tokens()

    def get_email(self, obj):
        """
        Return user's email based on provided username.
        """
        return User.objects.get(username=obj['username']).email

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
