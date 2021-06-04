from django.db import models
from django.utils.translation import gettext_lazy as _

from api.models import TimestampedModel


class Word(models.Model):
    id = models.CharField(primary_key=True, max_length=64)


class WordEntry(models.Model):
    class Meta:
        abstract = True

    id = models.CharField(primary_key=True, max_length=64)
    word = models.ForeignKey('dictionary.Word', on_delete=models.CASCADE)
    icon = models.ForeignKey(
        'dictionary.Icon', default=None, on_delete=models.CASCADE)


class DictionaryEntry(WordEntry):
    json = models.TextField(_('Merriam-Webster dictionary entry'), default='')


class ThesaurusEntry(WordEntry):
    json = models.TextField(_('Merriam-Webster thesaurus entry'), default='')
