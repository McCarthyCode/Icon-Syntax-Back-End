from django.db import models
from django.db.models.signals import post_save

from .image import Image


class Icon(Image):
    """
    Image file associated with zero or more WordEntries.
    """
    # Attributes
    is_approved = models.BooleanField(default=False)

    # Static variables
    __block_size = 2**12

    class InvalidImageError(Exception):
        """
        Exception to be raised when on icon does not meet specifications.
        """
        pass

    @classmethod
    def post_save(
            cls, sender, instance, created, raw, using, update_fields,
            **kwargs):
        """
        Method to perform preliminary operations just after instance creation.
        """
        if instance.image.width > 64 or instance.image.height > 54:
            instance.delete()
            raise Icon.InvalidImageError()


post_save.connect(Image.post_save, sender=Icon, dispatch_uid='0')
post_save.connect(Icon.post_save, sender=Icon, weak=False, dispatch_uid='1')
