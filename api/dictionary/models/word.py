import json
from collections import OrderedDict

from django.db import models
from django.utils.translation import gettext_lazy as _

from api.models import TimestampedModel


class Word(TimestampedModel):
    id = models.CharField(primary_key=True, max_length=64)

    @property
    def obj(self):
        dictionary = [x.obj for x in DictionaryEntry.objects.filter(word=self)]

        return OrderedDict({
            'word': self.id,
            'dictionary': dictionary,
        })


class WordEntry(TimestampedModel):
    class Meta:
        abstract = True

    id = models.CharField(primary_key=True, max_length=64)
    word = models.ForeignKey('dictionary.Word', on_delete=models.CASCADE)
    icon = models.ForeignKey(
        'dictionary.Icon',
        blank=True,
        null=True,
        default=None,
        on_delete=models.CASCADE)
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
                'icon': self.icon.base64() if self.icon else None,
                'mp3': self.mp3.base64() if self.mp3 else None,
                'data': json.loads(self.json),
            })


class DictionaryEntry(WordEntry):
    json = models.TextField(_('Merriam-Webster dictionary entry'), default='')


class ThesaurusEntry(WordEntry):
    json = models.TextField(_('Merriam-Webster thesaurus entry'), default='')
