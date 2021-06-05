import json
import requests

from django.conf import settings

from .models import Word, DictionaryEntry


class ExternalAPIManager:
    """
    Class defining utility methods for sending requests to external APIs.
    """
    __mw_dict_calls = 0

    @staticmethod
    def mw_dict_calls():
        """
        Static method returning the number of calls to the Merriam-Webster Collegiate Dictionary API since the value was last set or reset.
        """
        if settings.COUNT_API_CALLS:
            return ExternalAPIManager.__mw_dict_calls
        raise AttributeError(
            "type object 'ExternalAPIManager' has no attribute 'mw_dict_calls'")

    @staticmethod
    def reset_mw_dict_calls():
        """
        Static method resetting the number of calls to the Merriam-Webster Collegiate Dictionary API.
        """
        if settings.COUNT_API_CALLS:
            ExternalAPIManager.__mw_dict_calls = 0
        else:
            raise AttributeError(
                "type object 'ExternalAPIManager' has no attribute 'reset_mw_dict_calls'"
            )

    @staticmethod
    def get_mw_dict(word):
        """
        Method to query the Merriam-Webster collegiate dictionary API.
        """
        # breakpoint()
        if settings.COUNT_API_CALLS:
            ExternalAPIManager.__mw_dict_calls += 1

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

            response = ExternalAPIManager.get_mw_dict(word)

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
