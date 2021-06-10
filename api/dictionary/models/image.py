import hashlib
import os

from base64 import b16encode, b64encode
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
        blank=True, null=True, default=None, upload_to='img')
    _hash = models.BinaryField(
        editable=False, null=True, default=None, max_length=16)

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

    def base64(self, relative_path='img'):
        """
        Convert file to a base-64 string.
        """
        path = os.path.join(settings.MEDIA_ROOT, self.image.name)
        with open(path) as f:
            return b64encode(f.readlines())

    def __hash_image(self, relative_path, block_size=65536):
        """
        Create a MD5 cryptographic hash of the image, store it in the database, and rename the file.
        """
        hasher = hashlib.md5()
        filename = os.path.join(settings.MEDIA_ROOT, self.image.name)

        with open(filename, 'rb') as image:
            for buffer in iter(partial(image.read, block_size), b''):
                hasher.update(buffer)

            if not self._hash or \
            self._hash != hasher.hexdigest().lower():
                self._hash = hasher.digest()
                self.image.name = os.path.join(
                    relative_path,
                    hasher.hexdigest().lower())

                new_filename = os.path.join(
                    settings.MEDIA_ROOT, self.image.name)
                os.rename(filename, new_filename)

    @property
    def hash(self):
        """
        Get the image hash as a base-16 string.
        """
        return str(
            b16encode(self._hash).lower(), 'utf-8') if self._hash else None
