from django.db import models
from django.utils.translation import gettext_lazy as _

from api.models import TimestampedModel
from . import CharID

class DictionaryEntry(TimestampedModel, CharID):
    """
    TimestampedModel containing an ID for the word (and definition if a homograph), an Icon, an MP3 containing the word's pronunciation, and JSON data containing the response body for the entry.
    """
    icon = models.OneToOneField('Icon', on_delete=models.CASCADE)
    mp3 = models.OneToOneField(
        'MP3', verbose_name=_('MP3'), on_delete=models.CASCADE)
    data = models.TextField(_('JSON data'))
