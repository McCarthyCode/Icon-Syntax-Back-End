from django.contrib.auth.models import AnonymousUser

from rest_framework import serializers

from ..models import User


class PasswordForgotSerializer(serializers.ModelSerializer):
    """
    Serializer that validates an email address and returns its corresponding user if one exists.
    """
    class Meta:
        """
        The serializer's metaclass defining the type of model being serialized and any fields used for serialization I/O.
        """
        model = User
        fields = ['email']

    email = serializers.EmailField(
        label='Email Address', max_length=254, required=True, write_only=True)

    def validate_email(self, value):
        """
        Field-level validation method that queries the database for a User containing the specified email address, returning the original value on success and None on failure. This is also where the model instance is populated.
        """
        try:
            self.instance = User.objects.get(email=value)
        except User.DoesNotExist:
            self.instance = AnonymousUser
            return None

        return value

    def save(self, **kwargs):
        """
        Method that simply returns the model instance.
        """
        return self.instance
