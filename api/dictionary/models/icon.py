from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _

from .image import Image


class Icon(Image):
    """
    Image file associated with zero or more WordEntries.
    """
    # Attributes
    is_approved = models.BooleanField(default=False)

    # Static variables
    __block_size = 2**12

post_save.connect(Image.post_save, sender=Icon, dispatch_uid='0')
