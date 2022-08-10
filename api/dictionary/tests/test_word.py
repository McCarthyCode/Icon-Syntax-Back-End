import os

from django.conf import settings
from django.urls import reverse

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient, APITestCase

from api import NON_FIELD_ERRORS_KEY
from api.authentication.models import User
from api.tests.mixins import TestCaseShortcutsMixin

from ..models import Word, DictionaryEntry, Icon
from ..utils import DictionaryAPIManager


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

    relative_filepath = 'api/dictionary/tests/media/img/can.GIF'
    dict_entry_id = 'hammer:1'

    def setUp(self):
        # reset the counter
        DictionaryAPIManager.reset_num_api_calls()

    def test_options(self):
        """
        Ensure we can successfully get data from an OPTIONS request.

        TODO: detail request parameters
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

        self.assertEqual(DictionaryAPIManager.num_api_calls(), 1)
        self.assertIsNotNone(self.__get_word())
        self.assertEquals(
            len(self.__get_dict_entries()), self.search_word_entries)

        types = {
            'word': str,
            'dictionary': [dict],
            'thesaurus': None,
            'wordNet': None
        }
        self.assertDictTypes(response.data, types)

        dictionary = response.data['dictionary']
        for entry in dictionary:
            types = {'id': str, 'icons': [dict], 'mp3': dict, 'data': None}
            self.assertDictTypes(entry, types)

            for icon in entry['icons']:
                types = {'id': int, 'icon': str, 'md5': str}
                self.assertDictTypes(icon, types)

                regexes = {
                    'id': settings.INT_ID_REGEX,
                    'icon': settings.B64_REGEX,
                    'md5': settings.MD5_REGEX
                }
                for key, regex in regexes.items():
                    self.assertRegex(str(icon[key]), regex)

    def test_success_miss(self):
        """
        Ensure that we can query the Merriam-Webster dictionary API and populate our database when the entry is not in store.
        """
        # execution
        self.assertEqual(DictionaryAPIManager.num_api_calls(), 0)
        response = self.client.get(self.url_path, format='json')
        self.assertEqual(DictionaryAPIManager.num_api_calls(), 1)

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

    def test_success_hit_icon(self):
        """
        Ensure that if we upload an icon first, it shows in the response and the cached word entry associated with the uploaded icon is used.
        """
        # test-specific setup - upload an icon
        self.assertEqual(DictionaryAPIManager.num_api_calls(), 0)

        self.user = User.objects.create_superuser(
            'alice', 'alice@example.com', 'Easypass123!')

        self.spoof_verification()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user.access}')

        upload_url_path = reverse('api:dict:icon-upload')
        filepath = os.path.join(settings.BASE_DIR, self.relative_filepath)
        with open(filepath, 'rb') as f:
            data = {'icon': f, 'dictEntry': self.dict_entry_id}
            response = self.client.post(upload_url_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(DictionaryAPIManager.num_api_calls(), 1)

        values = {'success': 'File upload successful.'}
        self.assertDictEqual(values, response.data)

        self.assertTrue(Icon.objects.all().first().is_approved)

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
        self.search_word = 'qwert'
        self.url_path = f'/api/{settings.VERSION}/{self.search_word}'
        self.search_word_entries = 0

        # execution
        response = self.client.get(self.url_path, format='json')

        # test
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(DictionaryAPIManager.num_api_calls(), 1)
        self.assertIsNone(self.__get_word())
        word, entries = Word.objects.get_word_and_entries(self.search_word)

        self.assertIsNone(word)
        self.assertEquals(
            len(self.__get_dict_entries()), self.search_word_entries)

        values = {
            NON_FIELD_ERRORS_KEY:
            [ErrorDetail("Word 'qwert' not found.", code='not_found')]
        }
        self.assertDictValues(response.data, values)
