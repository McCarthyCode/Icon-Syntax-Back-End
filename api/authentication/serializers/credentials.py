import re
import jwt

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from ..models import User


class TokensSerializer(serializers.Serializer):
    """
    Serializer for displaying user tokens. Intended for use by CredentialsSerializer.
    """
    access = serializers.CharField(
        read_only=True, label='Access Token', required=False, max_length=256)
    refresh = serializers.CharField(
        read_only=True, label='Refresh Token', required=False, max_length=256)


class CredentialsSerializer(serializers.Serializer):
    """
    Serializer for displaying user credentials (username, email, and access/refresh tokens) based on an access token. Intended for use by any serializer .
    """
    username = serializers.CharField(max_length=64, required=False)
    email = serializers.EmailField(
        label='Email Address', max_length=254, required=False)
    password = serializers.CharField(
        min_length=8,
        max_length=64,
        write_only=True,
        required=False,
        style={'input_type': 'password'})
    tokens = TokensSerializer()
