import hashlib
import os
import requests
import string

from base64 import b16encode
from collections import OrderedDict
from functools import partial
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import NotFound

from api.exceptions import InternalServerError
from api.models import TimestampedModel
from api.dictionary.utils import ExternalAPIManager


class MP3Manager(models.Manager, ExternalAPIManager):
    """
    Class defining utility methods for downloading audio files from the Merriam-Webster media servers.
    """
    @classmethod
    def __get_mp3(cls, id):
        """
        Private class method that increments the API call counter and sends a GET request to the Merriam-Webster media servers for obtaining an MP3 file.
        """
        try:
            cls.increment_num_api_calls()
        except AttributeError:
            pass

        subdir = id[0]
        for substr in {'bix', 'gg'}:
            if id[:len(substr)] == substr:
                subdir = substr

        if subdir in string.punctuation + string.digits:
            subdir = 'number'

        return requests.get(
            f'https://media.merriam-webster.com/audio/prons/en/us/mp3/{subdir}/{id}.mp3'
        )


    @classmethod
    def get_mp3(cls, id):
        """
        Public wrapper for private method __get_mp3(). Obtains an MP3 file from local storage if a cache entry exists, and downloads from the Merriam-Webster database on a cache miss.
        """
        instance, created = MP3.objects.get_or_create(id=id)

        if created:
            response = cls.__get_mp3(id)
            if response.status_code in (status.HTTP_404_NOT_FOUND,
                                        status.HTTP_403_FORBIDDEN):
                raise NotFound(_('The specified ID was invalid.'))
            elif response.status_code != status.HTTP_200_OK:
                raise InternalServerError(
                    _(
                        'The file could not retrieved. Please contact support at support@iconsyntax.org.'
                    ))

            instance.mp3.save(
                f'{id}.mp3', ContentFile(response.content), save=False)
            instance.save()

        return instance


class MP3(TimestampedModel):
    """
    Timestamped model for MP3 pronunciation audio files downloaded from the Merriam-Webster media servers.
    """
    # Static Variables
    objects = MP3Manager()
    relative_path = 'mp3'
    block_size = 2**16

    # Attributes
    id = models.CharField(primary_key=True, max_length=64)
    mp3 = models.FileField(_('MP3'), upload_to=relative_path)
    _hash = models.BinaryField(
        _('MD5 hash'), editable=False, null=True, default=None, max_length=16)

    def __hash(self):
        """
        Create a MD5 cryptographic hash of the file, store it in the database, and rename the file.
        """
        hasher = hashlib.md5()
        working_dir = os.path.join(settings.MEDIA_ROOT, self.relative_path)
        filename = os.path.join(working_dir, f'{self.id}.mp3')

        try:
            with open(filename, 'rb') as data:
                for buffer in iter(partial(data.read, self.block_size), b''):
                    hasher.update(buffer)

                # Make changes if stored hash does not exist
                if not self._hash or self._hash != hasher.hexdigest().lower():
                    # Update hash and data name attributes
                    self._hash = hasher.digest()
                    self.mp3.name = os.path.join(
                        self.relative_path,
                        hasher.hexdigest().lower() + '.mp3')

                    # Save
                    post_save.disconnect(
                        MP3.post_save, sender=MP3, dispatch_uid='2')
                    self.save()
                    post_save.connect(
                        MP3.post_save, sender=MP3, dispatch_uid='2')

                    # Update filesystem
                    new_filename = os.path.join(
                        settings.MEDIA_ROOT, self.mp3.name)
                    os.rename(filename, new_filename)
        except FileNotFoundError:
            path = Path(working_dir)
            path.mkdir(parents=True, exist_ok=True)

            path = Path(filename)
            path.touch()

            self.__hash()

    @property
    def b64(self):
        """
        Convert the MP3 to a base-64 string.
        """
        from api.dictionary.utils import Base64Converter

        return Base64Converter.encode(self.mp3.name, block_size=self.block_size)

    @property
    def md5(self):
        """
        Get the MD5 audio hash as a base-16 string.
        """
        return str(
            b16encode(self._hash).lower(), 'utf-8') if self._hash else None

    @property
    def obj(self):
        """
        Property returning an OrderedDict with the following attributes: 'id', which contains the base filename, 'mp3', a base-64 string containing the MP3 file itself, and 'md5', an MD5 hash of the file for identification purposes.
        """
        return OrderedDict({'id': self.id, 'mp3': self.b64, 'md5': self.md5})

    @classmethod
    def post_save(
            cls, sender, instance, created, raw, using, update_fields,
            **kwargs):
        """
        Method to perform preliminary operations just after instance creation.
        """
        instance.__hash()

        empty_md5 = 'd41d8cd98f00b204e9800998ecf8427e'
        if instance.md5 == empty_md5:
            path = os.path.join(settings.MEDIA_ROOT, instance.mp3.name)
            if os.path.isfile(path):
                os.remove(path)

            post_save.disconnect(MP3.post_save, sender=MP3, dispatch_uid='2')
            instance.mp3.delete()
            post_save.connect(MP3.post_save, sender=MP3, dispatch_uid='2')


post_save.connect(MP3.post_save, sender=MP3, dispatch_uid='2')
