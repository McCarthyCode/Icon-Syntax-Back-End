import re
import jwt

from django.conf import settings
from django.contrib.auth import password_validation as validation
from django.utils.translation import gettext_lazy as _

from jwt.exceptions import DecodeError, ExpiredSignatureError

from rest_framework import serializers, status
from rest_framework.exceptions import ErrorDetail, ValidationError

from api.authentication import NON_FIELD_ERRORS_KEY

from ..exceptions import ConflictError
from ..models import User

from .credentials import CredentialsSerializer


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializes username, email, and password and creates users for use in registration.
    """
    class Meta():
        model = User
        fields = ['username', 'email', 'password']

    username = serializers.CharField(max_length=64)
    email = serializers.EmailField(label='Email Address', max_length=254)
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

        try:
            validation.validate_password(
                password=data.get('password'), user=user)
        except ValidationError as exc:
            raise ValidationError({'password': exc.detail})

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


class RegisterVerifySerializer(serializers.Serializer):
    """
    Serializes username, email, and tokens from an access token for marking a user as verified and logging them in.
    """
    credentials = CredentialsSerializer(read_only=True)

    default_error_messages = {
        'invalid': _('The activation link was invalid or has expired.'),
    }

    def validate(self, data):
        """
        Retrieve the user, mark their email address as verified, and return serialized data.
        """
        user = self.context['request'].user

        if user.is_anonymous:
            self.fail('invalid')

        return {'credentials': user.credentials}

    def save(self, **kwargs):
        """
        Retrieve the user, mark their email address as verified, and return the updated instance.
        """
        user = self.context['request'].user
        user.is_verified = True

        return user.save()
