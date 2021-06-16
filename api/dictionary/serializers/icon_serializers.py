from rest_framework import serializers
from ..models import Icon


class IconUploadSerializer(serializers.Serializer):
    """
    Serializer for the icon upload action. Defines write-only attribute icon.
    """
    icon = serializers.ImageField(write_only=True, required=True)


class IconApproveSerializer(serializers.Serializer):
    """
    Serializer for the icon approve action. Defines write-only attribute id.
    """
    id = serializers.IntegerField(write_only=True, required=True)


class IconRetrieveSerializer(serializers.ModelSerializer):
    """
    Serializer for the icon retrieve action. Defines read-only attributes id, icon, and md5.
    """
    class Meta:
        """
        Metaclass
        """
        model = Icon
        fields = ['id']
        read_only_fields = ['id']

    icon = serializers.CharField(max_length=16384, read_only=True)
    md5 = serializers.CharField(max_length=32, read_only=True)
