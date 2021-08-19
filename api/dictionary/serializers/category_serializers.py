from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ..models import Category


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the category create and update actions.
    """
    class Meta:
        """
        The meta definitions for the serializer class
        """
        model = Category
        fields = ['id', 'name', 'parent']

    def validate_parent(self, value):
        if value == None:
            return None

        try:
            Category.objects.get(pk=value.id)
        except Category.DoesNotExist:
            return None

        return value

    def create(self, validated_data):
        return Category.objects.create(**validated_data)
