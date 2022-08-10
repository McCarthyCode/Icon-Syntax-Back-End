from django.http import HttpResponseServerError
from django.shortcuts import get_object_or_404

from rest_framework import serializers, exceptions
from .models import Post

from api.authentication.models import User


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post.Comment
        fields = '__all__'
        read_only_fields = ['owner']

    owner = serializers.SerializerMethodField()

    def get_owner(self, obj: Post.Comment):
        if self.context['method'] == 'POST':
            owner: User = self.context['user']
            if not owner:
                raise HttpResponseServerError()

            return owner.obj

        elif self.context['method'] in ['PUT', 'PATCH']:
            if not obj.owner:
                raise HttpResponseServerError()
            owner: User = get_object_or_404(User, pk=obj.owner.pk)

            return owner.obj

        raise MethodNotAllowed(self.context['method'])

    def create(self, validated_data):
        owner: User = self.context['user']
        if not owner:
            raise HttpResponseServerError()

        validated_data['owner'] = owner

        return super().create(validated_data)
