import re
import jwt

from django.conf import settings
from django.contrib.auth import password_validation as validators
from django.utils.translation import gettext_lazy as _

from jwt.exceptions import DecodeError, ExpiredSignatureError

from rest_framework import serializers, status
from rest_framework.exceptions import ErrorDetail, ValidationError

from ..exceptions import ConflictError
from ..models import User

from .abstract import AuthAbstractSerializer


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
        min_length=8,
        max_length=64,
        write_only=True,
        style={'input_type': 'password'})

    default_error_messages = {
        'invalid':
        _('The activation link was invalid.'),
        'expired':
        _('The activation link has expired.'),
        'username_exists':
        _('A user with this username already exists. Please try again.'),
        'email_exists':
        _('A user with this email address already exists. Please try again.')
    }

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
                'username': [
                    ErrorDetail(
                        self.error_messages['username_exists'],
                        'username_exists')
                ]
            } if username_exists else {}
            email_dict = {
                'email': [
                    ErrorDetail(
                        self.error_messages['email_exists'], 'email_exists')
                ]
            } if email_exists else {}

            raise ConflictError({**username_dict, **email_dict})

        return super().validate(data)

    def create(self, validated_data):
        """
        Create the User object by passing validated_data to create_user method in manager.
        """
        return User.objects.create_user(**validated_data)


class RegisterVerifySerializer(AuthAbstractSerializer):
    """
    Serializes username, email, and tokens from an access token for logging in after verifying an email address.
    """
    default_error_messages = {
        'invalid': _('The activation link was invalid.'),
        'expired': _('The activation link has expired.'),
        'user_gone': _('The user associated with this token no longer exists.'),
    }

    def validate_access(self, value):
        """
        Validate the access token, checking against TOKEN_REGEX, and logout its associated user on success. On failure, raise a ValidationError exception with an appropriate error message.
        """
        try:
            assert re.match(settings.TOKEN_REGEX, value)
        except AssertionError:
            raise ValidationError(self.error_messages['invalid'], 'invalid')
        return value

    def validate(self, data):
        """
        Retrieve the user, mark their email address as verified, and return serialized data on success. On failure, the _get_user() method called by validate() will raise one of four possible exceptions, as outlined in the _get_user() docstring.
        """
        user = self._get_user(data)
        user.is_verified = True
        user.save()

        return data
