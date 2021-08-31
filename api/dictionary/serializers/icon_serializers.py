from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ..models import Word, Icon, DictionaryEntry, Category


class IconUploadSerializer(serializers.Serializer):
    """
    Serializer for the icon upload action. Defines write-only attribute icon.
    """
    icon = serializers.ImageField(write_only=True, required=True)
    word = serializers.CharField(required=True, max_length=80)
    descriptor = serializers.CharField(
        required=False, allow_null=True, max_length=80)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), required=True)

    def validate_icon(self, icon):
        if icon.image.width > 64 or icon.image.height > 54:
            raise ValidationError(
                _(
                    'The size of the uploaded image is invalid. Be sure to include an image of maximum width 64 pixels and exact height 54 pixels.'
                ), 'bad_request')

        return icon

    def save(self):
        icon = Icon.objects.create(
            image=self.validated_data['icon'],
            word=self.validated_data['word'],
            category=self.validated_data['category'],
        )
        should_save = False

        try:
            icon.descriptor = self.validated_data['descriptor']
            should_save = True
        except KeyError:
            pass

        if self.context['request'].user.is_superuser:
            icon.is_approved = True
            should_save = True

        if should_save:
            icon.save()

        return icon


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
        Metaclass defining the model as Icon and fields used as read-only field 'id'.
        """
        model = Icon
        fields = ['id']
        read_only_fields = ['id']

    icon = serializers.CharField(max_length=16384, read_only=True)
    md5 = serializers.CharField(min_length=32, max_length=32, read_only=True)
