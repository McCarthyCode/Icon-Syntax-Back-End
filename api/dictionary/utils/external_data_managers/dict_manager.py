import requests
from django.conf import settings
from .external_api_manager import ExternalAPIManager


class DictionaryAPIManager(ExternalAPIManager):
    """
    Class defining utility methods for sending requests to the external Merriam-Webster Collegiate Dictionary API.
    """
    @classmethod
    def get(cls, word):
        """
        Method to query the Merriam-Webster Collegiate Dictionary API.
        """
        try:
            cls.increment_num_api_calls()
        except AttributeError:
            pass

        return requests.get(
            f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={settings.MW_DICTIONARY_API_KEY}'
        )
