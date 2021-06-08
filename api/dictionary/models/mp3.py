from django.db import models
from django.utils.translation import gettext_lazy as _

from api.models import TimestampedModel


class MP3(TimestampedModel):
    # id = models.CharField(primary_key=True, max_length=64)
    data = models.FileField(_('MP3'), upload_to='mp3')

    def base64(self, relative_path='mp3'):
        """
        Convert file to a base-64 string.
        """
        with open(settings.MEDIA_ROOT / relative_path / self.data.name) as f:
            return b64encode(f.readlines())
