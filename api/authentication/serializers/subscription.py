from rest_framework import serializers
from ..models import Subscription


class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = '__all__'

    def create(self, validated_data):
        return Subscription.objects.get_or_create(**validated_data)[0]

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)

        return instance
