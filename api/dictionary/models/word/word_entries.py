import json
from collections import OrderedDict

from django.db import models
from django.utils.translation import gettext_lazy as _

from api.models import TimestampedModel


class WordEntry(TimestampedModel):
    """
    Timestamed, abstract model defining the data associated with a word. Has a string ID and foreign keys to Word, Icon, and MP3 models.
    """
    class Meta:
        """
        Metaclass defining the model as abstract.
        """
        abstract = True

    id = models.CharField(primary_key=True, max_length=64)
    word = models.ForeignKey('dictionary.Word', on_delete=models.CASCADE)
    icons = models.ManyToManyField('dictionary.Icon')
    mp3 = models.ForeignKey(
        'dictionary.MP3',
        blank=True,
        null=True,
        default=None,
        on_delete=models.CASCADE)

    @property
    def obj(self):
        return OrderedDict(
            {
                'id': self.id,
                'icons':
                [icon.obj for icon in self.icons.filter(is_approved=True)],
                'mp3': self.mp3.b64 if self.mp3 else None,
                'data': json.loads(self.json),
            })


class DictionaryEntry(WordEntry):
    """
    An entry pulled from the Merriam-Webster Collegiate Dictionary API. Contains all attributes and properties defined in WordEntry, along with the JSON data from the API.
    """
    json = models.TextField(_('Merriam-Webster dictionary entry'), default='')


class ThesaurusEntry(WordEntry):
    """
    An entry pulled from the Merriam-Webster Collegiate Thesaurus API. Contains all attributes and properties defined in WordEntry, along with the JSON data from the API.
    """
    json = models.TextField(_('Merriam-Webster thesaurus entry'), default='')
