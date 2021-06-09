from django.db import models
from django.db.models.signals import post_save

from api.models import TimestampedModel
from .image import Image


class Icon(TimestampedModel, Image):
    """
    Image file associated with zero or more WordEntries.
    """
    is_approved = models.BooleanField(default=False)

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

        # try:
        #     relative_path = kwargs['relative_path']
        # except KeyError:
        #     relative_path = 'img'

        # instance.image_ops(relative_path)

        instance.image_ops('img')


post_save.connect(Icon.post_save, sender=Icon, weak=False, dispatch_uid='0')
