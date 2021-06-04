from django.conf import settings
from django.urls import reverse

from rest_framework import status
# from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient, APITestCase

from api.test_mixins import TestCaseShortcutsMixin


class WordSearchTests(TestCaseShortcutsMixin, APITestCase):
    """
    Tests to check search endpoints. Checks against a hard-coded URL and a reverse-lookup name in nine tests, which check for an OPTIONS request and POST requests that validate user input.
    """
    client = APIClient()
    databases = {'default', 'admin_db'}

    search_word = 'hammer'
    url_name = 'api:dict:search'
    url_path = f'/api/{settings.VERSION}/search/{search_word}'

    reverse_kwargs = {'word': search_word}

    def test_options(self):
        """
        Ensure we can successfully get data from an OPTIONS request.
        """
        response = self.client.options(self.url_path, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertDictTypes(response.data, self.options_types)

    def __test_success(self, response):
        """
        Ensure that we can query the Merriam-Webster dictionary API and populate our database.
        """
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        types = {
            'results': [dict],
            'pagination': {
                'totalResults': int,
                'maxResultsPerPage': int,
                'numResultsThisPage': int,
                'thisPageNumber': int,
                'totalPages': int,
                'prevPageExists': int,
                'nextPageExists': int,
            }
        }

        self.assertDictTypes(response.data, types)

        types = {'id': str, 'sort': str, 'stems': [str], 'offensive': bool}

        for result in response.data['results']:
            self.assertDictTypes(result, types)

    def test_success_miss(self):
        """
        Ensure that we can query the Merriam-Webster dictionary API and populate our database when the entry is not in store.
        """
        # self.assertIsNone(Word)
        response = self.client.get(self.url_path, format='json')
        self.__test_success(response)

    def test_success_hit(self):
        """
        Ensure that we can use the entry in store if one exists.
        """
        for _ in range(2):
            response = self.client.get(self.url_path, format='json')
        self.__test_success(response)
