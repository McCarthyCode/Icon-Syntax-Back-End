import json
import requests

from django.conf import settings

from ..models.word import Word, DictionaryEntry


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
    def get_word_and_entries(word):
        """
        Method to obtain a word and its corresponding dictionary entries from the local database, creating them if they don't exist.

        Returns a two-tuple containing (a) the Word object on a hit or a near miss, and None for any other input, and (b) the list of dictionary entries, None, or a list of suggestions.
        """
        _word = None

        try:
            _word = Word.objects.get(id=word)
        except Word.DoesNotExist:
            _word = Word.objects.create(id=word)

            response = ExternalAPIManager.get_mw_dict(word)
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
