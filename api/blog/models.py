from collections import OrderedDict
from django.db import models
from api.models import TimestampedModel
from api.authentication.models import User


class Post(TimestampedModel):
    title = models.CharField(max_length=80)
    content = models.TextField()
    owner = models.ForeignKey(
        User, default=None, null=True, on_delete=models.CASCADE)

    class Comment(TimestampedModel):
        post = models.ForeignKey('Post', on_delete=models.CASCADE)
        content = models.TextField()
        parent = models.ForeignKey(
            'Comment', null=True, on_delete=models.CASCADE)
        owner = models.ForeignKey(
            User, default=None, null=True, on_delete=models.SET_NULL)

        @property
        def obj(self):
            queryset = Post.Comment.objects.filter(
                post__pk=self.post.id, parent__pk=self.id)
            comments = [x.obj for x in queryset]

            return OrderedDict(
                {
                    'id': self.id,
                    'post': self.post.pk,
                    'content': self.content,
                    'replies': comments,
                    'owner': self.owner.pk if self.owner else None,
                    'created': self.created,
                    'updated': self.updated
                })

    @property
    def obj(self):
        queryset = Comment.objects.filter(post__pk=self.id, parent=None)
        comments = [x.obj for x in queryset]

        return OrderedDict(
            {
                'id': self.id,
                'title': self.title,
                'content': self.content,
                'comments': comments,
                'created': self.created,
                'updated': self.updated
            })
