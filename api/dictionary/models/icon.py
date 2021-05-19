from django.db import models
from django.utils.translation import gettext_lazy as _

from api.models import TimestampedModel

from .category import CATEGORY_CHOICES
from .char_id import CharID
from .image import Image


class Icon(TimestampedModel, Image, CharID):
    """
    TimestampedModel containing an ID for the word (and definition if a homograph), an Image, and the category for the Icon
    """
    category = models.SmallIntegerField(choices=CATEGORY_CHOICES)
