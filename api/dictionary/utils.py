import json
import requests

from django.conf import settings

from .models import Word, DictionaryEntry


class Util:
    """
    Class defining utility methods for the dictionary app.
    """
    @staticmethod
    def get_mw_dict(word):
        """
        Method to query the Merriam-Webster collegiate dictionary API.
        """
        return requests.get(
            f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={settings.MW_DICTIONARY_API_KEY}'
        )

    @staticmethod
    def get_mw_thes(word):
        """
        Method to query the Merriam-Webster collegiate thesaurus API.
        """
        pass

    @staticmethod
    def get_wn(word):
        """
        Method to obtain data from the Princeton WordNet library.
        """
        pass

    @staticmethod
    def get_word(word):
        """
        Method to obtain a word from the local database, creating one if it doesn't exist.
        """
        _word = None

        try:
            _word = Word.objects.get(id=word)
        except Word.DoesNotExist:
            _word = Word.objects.create(id=word)

            response = requests.get(
                f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={settings.MW_DICTIONARY_API_KEY}'
            )

            mw_dict_entries = filter(
                lambda x: word == x['meta']['id'].split(':')[0],
                json.loads(response.text),
            )

            for entry in mw_dict_entries:
                DictionaryEntry.objects.create(
                    id=entry['meta']['id'], word=_word, json=json.dumps(entry))

        return {
            'word': _word.id,
            'dictionaryEntries': DictionaryEntry.objects.filter(word=_word)
        }
