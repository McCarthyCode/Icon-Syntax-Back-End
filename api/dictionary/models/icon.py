from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _

from .image import Image


class Icon(Image):
    """
    Image file associated with zero or more WordEntries.
    """
    TENSE_CHOICES = [
        (None, 0),
        ('1', 1),  # present
        ('c', 2),  # present participle
        ('p', 3),  # past
        ('pp', 4),  # past participle
    ]

    # Attributes
    word = models.CharField(max_length=32)
    descriptor = models.CharField(blank=True, null=True, max_length=32)
    tense = models.PositiveSmallIntegerField(
        blank=True, null=True, default=None, choices=TENSE_CHOICES)
    is_approved = models.BooleanField(default=False)

    # Static variables
    block_size = 2**12


post_save.connect(Image.post_save, sender=Icon, dispatch_uid='0')
