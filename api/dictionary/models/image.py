import hashlib
import os

from base64 import b16encode, b64encode
from collections import OrderedDict
from functools import partial
from io import BytesIO
from PIL import Image

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _

from api.models import TimestampedModel
from ..utils import Base64Converter


class Image(TimestampedModel):
    """
    Abstract model containing an image, a hash of that image, and operation methods.
    """
    class Meta:
        """
        The metaclass defining its parent as abstract.
        """
        abstract = True

    # Static variables
    __relative_path = 'img'
    block_size = 2**16

    # Attributes
    image = models.ImageField(
        blank=True, null=True, default=None, upload_to=__relative_path)
    _hash = models.BinaryField(
        _('MD5 hash'), editable=False, null=True, default=None, max_length=16)

    def __str__(self):
        """
        The value of the class instance when typecast as a string.
        """
        return self.image.name

    def __hash(self):
        """
        Create a MD5 cryptographic hash of the image, store it in the database, and rename the file.
        """
        hasher = hashlib.md5()
        filename = os.path.join(settings.MEDIA_ROOT, self.image.name)

        with open(filename, 'rb') as image:
            for buffer in iter(partial(image.read, self.block_size), b''):
                hasher.update(buffer)

            # Make changes if stored hash does not exist
            if not self._hash or self._hash != hasher.hexdigest().lower():
                # Update hash and image name attributes
                self._hash = hasher.digest()
                self.image.name = os.path.join(
                    self.__relative_path,
                    hasher.hexdigest().lower())

                # Save
                from ..models import Icon
                post_save.disconnect(
                    Image.post_save, sender=Icon, dispatch_uid='0')
                post_save.disconnect(
                    Icon.post_save, sender=Icon, dispatch_uid='1')

                self.save()

                post_save.connect(
                    Image.post_save, sender=Icon, dispatch_uid='0')
                post_save.connect(Icon.post_save, sender=Icon, dispatch_uid='1')

                # Update filesystem
                new_filename = os.path.join(
                    settings.MEDIA_ROOT, self.image.name)
                os.rename(filename, new_filename)

    @property
    def b64(self):
        """
        Convert the image to a base-64 string.
        """
        return Base64Converter.encode(
            self.image.name, block_size=self.block_size)

    @property
    def md5(self):
        """
        Get the MD5 image hash as a base-16 string.
        """
        return str(
            b16encode(self._hash).lower(), 'utf-8') if self._hash else None

    @property
    def obj(self):
        """
        Serialize relevant fields and properties for JSON output.
        """
        return OrderedDict(
            {
                'id': self.id,
                'icon': self.b64,
                'md5': self.md5,
            })

    @classmethod
    def post_save(
            cls, sender, instance, created, raw, using, update_fields,
            **kwargs):
        """
        Method to perform preliminary operations just after instance creation.
        """
        instance.__hash()
