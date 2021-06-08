from django.conf import settings
from django.urls import reverse

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient, APITestCase

from api import NON_FIELD_ERRORS_KEY
from api.test_mixins import TestCaseShortcutsMixin

from ..models import Word, DictionaryEntry
from ..utils import ExternalAPIManager


class WordTests(TestCaseShortcutsMixin, APITestCase):
    """
    Tests to check word endpoints. Checks against a hard-coded URL and a reverse-lookup name in nine tests, which check for an OPTIONS request and POST requests that validate user input.
    """
    client = APIClient()
    databases = {'default', 'admin_db'}

    search_word = 'hammer'
    search_word_entries = 2

    url_name = 'api:dict:word'
    url_path = f'/api/{settings.VERSION}/{search_word}'

    reverse_kwargs = {'word': search_word}

    def setUp(self):
        # reset the counter
        ExternalAPIManager.reset_mw_dict_calls()

    def test_options(self):
        """
        Ensure we can successfully get data from an OPTIONS request.
        """
        response = self.client.options(self.url_path, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertDictTypes(response.data, self.options_types)

    def __get_word(self):
        try:
            self.word = Word.objects.get(id=self.search_word)
        except Word.DoesNotExist:
            self.word = None

        return self.word

    def __get_dict_entries(self):
        return DictionaryEntry.objects.filter(word=self.word)

    def __check_dict_entries(self):
        for entry in self.__get_dict_entries():
            self.assertIsInstance(entry, DictionaryEntry)
            self.assertIsInstance(entry.json, str)
            self.assertGreater(len(entry.json), 0)

    def __test_success(self, response):
        """
        Ensure that we can query the Merriam-Webster dictionary API and populate our database.
        """
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(ExternalAPIManager.mw_dict_calls(), 1)
        self.assertIsNotNone(self.__get_word())
        self.assertEquals(
            len(self.__get_dict_entries()), self.search_word_entries)

        types = {'word': str, 'dictionary': [dict]}

        self.assertDictTypes(response.data, types)

    def test_success_miss(self):
        """
        Ensure that we can query the Merriam-Webster dictionary API and populate our database when the entry is not in store.
        """
        # execution
        # reverse_kwargs = {}
        response = self.client.get(self.url_path, format='json')

        # test
        self.__test_success(response)

    def test_success_hit(self):
        """
        Ensure that we can use the entry in store if one exists.
        """
        # test-specific setup - initial call to ensure a db entry exists
        self.client.get(self.url_path, format='json')
        self.assertIsNotNone(self.__get_word())
        self.assertEquals(
            len(self.__get_dict_entries()), self.search_word_entries)

        # execution
        response = self.client.get(self.url_path, format='json')

        # test
        self.__test_success(response)

    def test_invalid_word(self):
        """
        Ensure that we can get a 404 response for an invalid word.
        """
        # test-specific setup
        # defining a different search word than the default
        self.search_word = 'qwertyuiop'
        self.url_path = f'/api/{settings.VERSION}/{self.search_word}'
        self.search_word_entries = 0

        # execution
        response = self.client.get(self.url_path, format='json')

        # test
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(ExternalAPIManager.mw_dict_calls(), 1)
        self.assertIsNotNone(self.__get_word())
        self.assertIsNone(ExternalAPIManager.get_word(self.search_word))
        self.assertEquals(
            len(self.__get_dict_entries()), self.search_word_entries)

        values = {
            NON_FIELD_ERRORS_KEY:
            [ErrorDetail("Word 'qwertyuiop' not found.", code='not_found')]
        }
        self.assertDictValues(response.data, values)
