from rest_framework import serializers
from .models import Post


class PostSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField('get_comments', read_only=True)

    class Meta:
        model = Post
        fields = '__all__'

    def get_comments(self, instance):
        queryset = Post.Comment.objects.filter(
            post__pk=instance.id, parent__pk=None)

        return [x.obj for x in queryset]


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post.Comment
        fields = '__all__'
