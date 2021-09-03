from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers


class PasswordForgotVerifySerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        validate_password(value, self.context['user'])

        return value

    def save(self):
        self.context['user'].password = make_password(
            self.validated_data['password'])
        self.context['user'].save()

        return self.context['user']
