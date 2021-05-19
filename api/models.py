from django.db import models
from django.utils.translation import gettext_lazy as _


class TimestampedModel(models.Model):
    """
    An abstract model with timestamps.
    """
    class Meta:
        """
        The metaclass defining its parent as abstract.
        """
        abstract = True

    created = models.DateTimeField(_('datetime created'), auto_now_add=True)
    updated = models.DateTimeField(_('datetime updated'), auto_now=True)
