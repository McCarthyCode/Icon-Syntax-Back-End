from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from api.authentication import NON_FIELD_ERRORS_KEY
from api.authentication.models import User

from .credentials import CredentialsSerializer


class PasswordResetSerializer(serializers.Serializer):
    oldPassword = serializers.CharField(
        write_only=True,
        label='Old Password',
        min_length=8,
        max_length=64,
    )
    newPassword = serializers.CharField(
        write_only=True,
        label='New Password',
        min_length=8,
        max_length=64,
    )
    credentials = CredentialsSerializer(read_only=True)

    default_error_messages = {
        'invalid':
        _('The authorization token was missing or invalid.'),
        'mismatch':
        _(
            'The old password was not correct. If you have forgotten your password, please use the "forgot password" link.'
        ),
        'user_gone':
        _('The user with the provided credentials could not be found.')
    }

    def validate_oldPassword(self, value):
        """
        Check if user is anonymous and to see if the password provided matches the one in the database. On success, return the raw password value. On failure, raise a validation error.
        """
        user = self.context['user']

        if user.is_anonymous:
            raise AuthenticationFailed(
                {NON_FIELD_ERRORS_KEY: [self.error_messages['invalid']]},
                'invalid')

        if user.check_password(value):
            return value

        raise AuthenticationFailed(
            {NON_FIELD_ERRORS_KEY: [self.error_messages['mismatch']]},
            'mismatch')

    def validate_newPassword(self, value):
        """
        Check if user is anonymous and to see if the password provided passes validation checks. On success, return the raw password value. On failure, raise a validation error.
        """
        user = self.context['user']

        if user.is_anonymous:
            raise AuthenticationFailed(
                {NON_FIELD_ERRORS_KEY: [self.error_messages['invalid']]},
                'invalid')

        validate_password(password=value, user=self.context['user'])

        return value

    def save(self, **kwargs):
        """
        Check if user is anonymous. If not, save the new password value in the database.
        """
        user = self.context['user']

        if user.is_anonymous:
            AuthenticationFailed(
                {NON_FIELD_ERRORS_KEY: [self.error_messages['invalid']]},
                'invalid')

        user.set_password(self.validated_data['newPassword'])
        user.save()

        return user.credentials
