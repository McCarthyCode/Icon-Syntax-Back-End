import requests
from django.conf import settings


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
