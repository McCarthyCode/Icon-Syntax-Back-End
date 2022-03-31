from collections import OrderedDict
from django.db import models
from api.models import TimestampedModel


class Category(TimestampedModel):
    name = models.CharField(max_length=40)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='children',
        on_delete=models.CASCADE)

    @property
    def path(self):
        if self.parent:
            if self.parent.path:
                return self.parent.path + ' » ' + self.parent.name
            else:
                return self.parent.name

        return ''

    def __str__(self):
        if self.parent:
            return self.path + ' » ' + self.name

        return self.name

    @property
    def obj(self):
        def common(obj):
            return OrderedDict(
                {
                    'id': obj.id,
                    'name': obj.name,
                    'path': obj.path,
                    'parent': obj.parent.id if obj.parent else None,
                })

        children = [
            OrderedDict({
                **common(x),
            }) for x in Category.objects.filter(parent=self)
        ]

        return OrderedDict({**common(self), 'children': children})

    @classmethod
    def subcategories(cls, root_id=0):
        if root_id == 0:
            return cls.objects.all()

        category = cls.objects.get(id=root_id)
        subcategories = [category]
        for subcategory in cls.objects.filter(parent=category.id):
            subcategories += cls.subcategories(subcategory.id)

        return subcategories

    def save(self, *args, **kwargs):
        # prevent a category to be its own parent
        if self.id and self.parent and self.id == self.parent.id:
            self.parent = None

        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Categories'