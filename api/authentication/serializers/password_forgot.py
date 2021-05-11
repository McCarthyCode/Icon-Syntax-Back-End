from django.contrib.auth.models import AnonymousUser

from rest_framework import serializers

from ..models import User


class PasswordForgotSerializer(serializers.ModelSerializer):
    """
    Serializer that validates an email address and returns its corresponding user if one exists.
    """
    class Meta:
        model = User
        fields = ['email']

    email = serializers.EmailField(
        label='Email Address', max_length=254, required=True, write_only=True)

    def validate_email(self, value):
        try:
            self.instance = User.objects.get(email=value)
        except User.DoesNotExist:
            self.instance = AnonymousUser
            return None

        return value

    def save(self, **kwargs):
        return self.instance
