from rest_framework import viewsets

from ..models import Post
from ..serializers import CommentSerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Post.Comment.objects.all()

    def get_queryset(self, *args, **kwargs):
        self.queryset = Post.Comment.objects.filter(*args, **kwargs)
        return self.queryset
