import hashlib
import os

from base64 import b16encode
from functools import partial
from io import BytesIO
from PIL import Image

from django.conf import settings
from django.db import models


class Image(models.Model):
    """
    Abstract model containing an image, a hash of that image, and operation methods.
    """
    class Meta:
        """
        The metaclass defining its parent as abstract.
        """
        abstract = True

    image = models.ImageField(
        blank=True, null=True, default=None, upload_to='icons')
    _hash = models.BinaryField(
        editable=False, null=True, default=None, max_length=16)

    @classmethod
    def create(cls, relative_path='', *args, **kwargs):
        """
        Method to upload an image and to perform preliminary operations.
        """
        image = cls(**kwargs)
        self.image_ops(relative_path)

        return image

    def __str__(self):
        """
        The value of the class instance when typecast as a string.
        """
        return self.image.name

    def image_ops(self, relative_path=''):
        """
        Image operations to be run when an image is added or updated.
        """
        self.__hash_image(relative_path)

    def __hash_image(self, relative_path, block_size=65536):
        """
        Create a MD5 cryptographic hash of the image, store it in the database, and rename the file.
        """
        hasher = hashlib.md5()
        filename = settings.MEDIA_ROOT / relative_path / self.image.name

        with open(filename, 'rb') as image:
            for buffer in iter(partial(image.read, block_size), b''):
                hasher.update(buffer)

            if not self._hash or \
            self._hash != hasher.hexdigest().lower():
                self._hash = hasher.digest()
                self.image.name = relative_path + hasher.hexdigest().lower()
                new_filename = \
                    settings.MEDIA_ROOT / relative_path / self.image.name
                os.rename(filename, new_filename)

    @property
    def image_hash(self):
        """
        Get the image hash as a base-16 string.
        """
        return str(
            b16encode(self._hash).lower(),
            'utf-8') if self._hash else None