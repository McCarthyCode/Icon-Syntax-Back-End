from django.db import models
from django.utils.translation import gettext_lazy as _

from api.models import TimestampedModel


class MP3(TimestampedModel):
    # Static Variables
    __relative_path = 'mp3'
    __block_size = 2 ** 16

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
