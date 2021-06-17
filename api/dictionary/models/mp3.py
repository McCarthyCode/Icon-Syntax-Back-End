import requests
import string

from django.db import models
from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import NotFound

from api.models import TimestampedModel
from api.dictionary.utils import ExternalAPIManager


class MP3Manager(models.Manager):
    """
    Class defining utility methods for downloading audio files from the Merriam-Webster media servers.
    """
    @staticmethod
    def __get_mp3(id):
        """
        Private method for obtaining a MP3 file from the Merriam-Webster media servers.
        """
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
        Public wrapper for private method __get_mp3(). Obtains a MP3 file from local storage if a cache entry exists, and downloads from the Merriam-Webster database on a cache miss.
        """
        mp3 = None

        try:
            mp3 = MP3.objects.get(id=id)
        except MP3.DoesNotExist:
            response = cls.__get_mp3(id)
            if response.status_code in {status.HTTP_404_NOT_FOUND,
                                        status.HTTP_403_FORBIDDEN}:
                raise NotFound('The specified ID was invalid.')
            elif response.status_code != status.HTTP_200_OK:
                raise

            mp3 = MP3.objects.create(id=id)

        return mp3


class MP3(TimestampedModel):
    """
    TODO
    """
    # Static Variables
    objects = MP3Manager()
    __relative_path = 'mp3'
    __block_size = 2**16

    # Attributes
    id = models.CharField(primary_key=True, max_length=64)
    data = models.FileField(_('MP3'), upload_to=__relative_path)

    @property
    def b64(self):
        """
        Convert the MP3 to a base-64 string.
        """
        from api.dictionary.utils import Base64Converter

        return Base64Converter.encode(
            self.image.name, block_size=self.__block_size)
