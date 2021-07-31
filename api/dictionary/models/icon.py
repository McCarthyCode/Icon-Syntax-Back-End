from collections import OrderedDict
from itertools import chain

from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _

from api.models import TimestampedModel
from .image import Image
from .category import Category


class Icon(Image):
    """
    Image file associated with a word, a descriptor, a part of speech, and (for verbs) tense.
    """

    # Static variables
    BLOCK_SIZE = 2**12

    # Attributes
    word = models.CharField(max_length=80)
    descriptor = models.CharField(blank=True, null=True, max_length=80)
    category = models.ForeignKey(
        Category, blank=True, null=True, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)

    @property
    def obj(self):
        """
        Serialize relevant fields and properties for JSON output.
        """
        return OrderedDict(
            {
                'id': self.id,
                'word': self.word,
                'descriptor': self.descriptor,
                'icon': self.b64,
                'md5': self.md5,
            })

    @classmethod
    def by_category(cls, category_id, filter_kwargs={}):
        querysets = []
        for category in Category.subcategories(category_id):
            querysets.append(
                cls.objects.filter(category=category, **filter_kwargs))

        return list(chain(*querysets))


post_save.connect(Image.post_save, sender=Icon, dispatch_uid='0')
