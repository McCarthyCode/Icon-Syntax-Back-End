from collections import OrderedDict
from django.db import models
from api.models import TimestampedModel


class Post(TimestampedModel):
    title = models.CharField(max_length=80)
    content = models.TextField()

    class Comment(TimestampedModel):
        post = models.ForeignKey('Post', on_delete=models.CASCADE)
        content = models.TextField()
        parent = models.ForeignKey(
            'Comment', null=True, on_delete=models.SET_NULL)

    @property
    def obj(self):
        return OrderedDict(
            {
                'title': self.title,
                'content': self.content,
                'created': self.created,
                'updated': self.updated
            })
