from rest_framework import serializers


class IconUploadSerializer(serializers.Serializer):
    icon = serializers.ImageField(write_only=True, required=True)
