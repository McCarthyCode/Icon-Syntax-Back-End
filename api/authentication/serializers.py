import django.contrib.auth.password_validation as validators

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from rest_framework import serializers

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializes username, email, and password and creates users for use in registration.
    """
    password = serializers.CharField(min_length=8, write_only=True)

    class Meta():
        model = User
        fields = ['username', 'email', 'password']

    def validate(self, data):
        """
        Check password against built-in validators.
        """
        # PUT, PATCH
        if self.instance:
            user = self.instance
            for key, value in data:
                user[key] = value
        # POST
        else:
            user = User(**data)

        validators.validate_password(password=data.get('password'), user=user)

        return super().validate(data)

    def create(self, validated_data):
        """
        Create the User object by passing validated_data to create_user method in manager.
        """
        return User.objects.create_user(**validated_data)
