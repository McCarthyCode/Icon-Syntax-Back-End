from django.db import models
from django.utils.translation import gettext_lazy as _

from api.models import TimestampedModel
from .char_id import CharID


class MP3(TimestampedModel, CharID):
    data = models.FileField(_('MP3'), upload_to='mp3')
