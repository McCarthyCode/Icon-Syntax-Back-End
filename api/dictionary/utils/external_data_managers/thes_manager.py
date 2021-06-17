import requests
from .external_api_manager import ExternalAPIManager


class ThesaurusAPIManager(ExternalAPIManager):
    """
    Class defining utility methods for sending requests to the external Merriam-Webster Collegiate Thesaurus API.
    """
    @classmethod
    def __get(cls, id):
        """
        Private method to query the Merriam-Webster Collegiate Thesaurus API.

        TODO: Pull data from the thesaurus.
        """
        try:
            cls.increment_num_api_calls()
        except AttributeError:
            pass

        # return requests.get(
        #     f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={settings.MW_DICTIONARY_API_KEY}'
        # )
