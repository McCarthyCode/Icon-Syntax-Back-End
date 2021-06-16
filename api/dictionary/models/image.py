import hashlib
import os

from base64 import b16encode, b64encode
from functools import partial
from io import BytesIO
from PIL import Image

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save

from api.models import TimestampedModel


class Image(TimestampedModel):
    """
    Abstract model containing an image, a hash of that image, and operation methods.
    """
    class Meta:
        """
        The metaclass defining its parent as abstract.
        """
        abstract = True

    # Attributes
    image = models.ImageField(
        blank=True, null=True, default=None, upload_to='img')
    _hash = models.BinaryField(
        editable=False, null=True, default=None, max_length=16)

    # Static variables
    block_size = 2 ** 16

    def __str__(self):
        """
        The value of the class instance when typecast as a string.
        """
        return self.image.name

    def image_ops(self, relative_path='img'):
        """
        Image operations to be run when an image is added or updated.
        """
        self.__hash_image(relative_path)

    def __hash_image(self, relative_path, block_size=65536):
        """
        Create a MD5 cryptographic hash of the image, store it in the database, and rename the file.
        """
        hasher = hashlib.md5()
        filename = os.path.join(settings.MEDIA_ROOT, self.image.name)

        with open(filename, 'rb') as image:
            for buffer in iter(partial(image.read, block_size), b''):
                hasher.update(buffer)

            # Make changes if stored hash does not exist
            if not self._hash or self._hash != hasher.hexdigest().lower():
                # Update hash and image name attributes
                self._hash = hasher.digest()
                self.image.name = os.path.join(
                    relative_path,
                    hasher.hexdigest().lower())

                # Save
                from ..models import Icon
                post_save.disconnect(
                    Image.post_save, sender=Icon, dispatch_uid='0')
                self.save()
                post_save.connect(
                    Image.post_save, sender=Icon, dispatch_uid='0')

                # Update filesystem
                new_filename = os.path.join(
                    settings.MEDIA_ROOT, self.image.name)
                os.rename(filename, new_filename)

    @property
    def b64(self):
        """
        Convert file to a base-64 string.
        """
        path = os.path.join(settings.MEDIA_ROOT, self.image.name)
        with open(path, 'rb') as image:
            byte_stream = b''
            for buffer in iter(partial(image.read, self.block_size), b''):
                byte_stream += buffer
            return str(b64encode(byte_stream), 'utf-8')

        return None

    @property
    def hash(self):
        """
        Get the MD5 image hash as a base-16 string.
        """
        return str(
            b16encode(self._hash).lower(), 'utf-8') if self._hash else None

    @classmethod
    def post_save(
            cls, sender, instance, created, raw, using, update_fields,
            **kwargs):
        """
        Method to perform preliminary operations just after instance creation.
        """
        instance.image_ops()
