from django.db import models
from django.utils.translation import gettext_lazy as _

from api.models import TimestampedModel


class Word(TimestampedModel):
    id = models.CharField(primary_key=True, max_length=64)


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


class DictionaryEntry(WordEntry):
    json = models.TextField(_('Merriam-Webster dictionary entry'), default='')


class ThesaurusEntry(WordEntry):
    json = models.TextField(_('Merriam-Webster thesaurus entry'), default='')
