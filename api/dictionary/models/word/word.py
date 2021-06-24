import json
from collections import OrderedDict
from django.db import models

from api.models import TimestampedModel
from api.dictionary.utils import DictionaryAPIManager, ThesaurusAPIManager

from .word_entries import DictionaryEntry, ThesaurusEntry


class WordManager(models.Manager):
    """
    Manager containing a method to pull Word data locally or remotely, depending on what's in store.
    """
    @staticmethod
    def get_word_and_entries(word):
        """
        Static method to obtain a word and its corresponding dictionary entries from the local database, creating them if they don't exist.

        Returns a two-tuple containing (a) the Word object on a hit or a near miss, and None for any other input, and (b) the list of dictionary entries, None, or a list of suggestions.

        TODO: Add thesaurus and WordNet entries
        """
        _word = None

        try:
            _word = Word.objects.get(id=word)
        except Word.DoesNotExist:
            _word = Word.objects.create(id=word)

            response = DictionaryAPIManager.get(word)
            data = json.loads(response.text)

            if type(data) != list or len(data) == 0:
                return None, []
            elif type(data[0]) == str:
                _word.delete()
                return None, data
            else:
                mw_dict_entries = filter(
                    lambda x: word == x['meta']['id'].split(':')[0], data)

                for entry in mw_dict_entries:
                    DictionaryEntry.objects.create(
                        id=entry['meta']['id'],
                        word=_word,
                        json=json.dumps(entry),
                    )

        return _word, DictionaryEntry.objects.filter(word=_word)


class Word(TimestampedModel):
    """
    Timestamped model for a single word object. Contains a character ID and the property "obj", which includes all and any associated data.
    """
    # Static Variables
    objects = WordManager()

    # Attributes
    id = models.CharField(primary_key=True, max_length=64)

    @property
    def obj(self):
        """
        Property returning an OrderedDict with the following attributes: 'word', which contains the word as a string, 'dictionary', a list of dictionary entries, 'thesaurus', a list of thesaurus entries, 'word-net', data from the Princeton WordNet library.
        """
        dictionary = [x.obj for x in DictionaryEntry.objects.filter(word=self)]

        return OrderedDict(
            {
                'word': self.id,
                'dictionary': dictionary,
                'thesaurus': None,
                'word-net': None,
            })
