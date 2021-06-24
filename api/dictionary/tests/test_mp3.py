from django.conf import settings
from django.urls import reverse

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient, APITestCase

from api import NON_FIELD_ERRORS_KEY
from api.tests.mixins import TestCaseShortcutsMixin

from ..models import MP3


class MP3Tests(TestCaseShortcutsMixin, APITestCase):
    """
    Tests to check MP3 endpoints. Checks against a hard-coded URL and a reverse-lookup name in nine tests, which check for an OPTIONS request and POST requests that validate user input.
    """
    client = APIClient()
    databases = {'default', 'admin_db'}

    test_id = 'apple001'

    url_name = 'api:dict:audio'
    url_path = f'/api/{settings.VERSION}/audio/{test_id}.mp3'

    reverse_kwargs = {'id': test_id}

    def setUp(self):
        """
        Reset the API counter
        """
        MP3.objects.reset_num_api_calls()

    def test_options(self):
        """
        Ensure that we get a proper response on an OPTIONS request.

        TODO: detail request parameters
        """
        response = self.client.options(self.url_path, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # types = {**self.options_types, 'actions': {'GET': {}}}
        self.assertDictTypes(response.data, self.options_types)

    def __success(self):
        """
        Helper method for use in tests where a success response is expected.
        """
        response = self.client.get(self.url_path, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        types = {'id': str, 'mp3': str, 'md5': str}
        self.assertDictTypes(response.data, types)

        regexes = {
            'id': settings.STR_ID_REGEX,
            'mp3': settings.B64_REGEX,
            'md5': settings.MD5_REGEX,
        }
        for key, value in regexes.items():
            self.assertRegex(str(response.data[key]), value)

    def test_success_miss(self):
        """
        Ensure that if a local copy of the requested MP3 is not present, we can save a copy and serialize the data in a response.
        """
        self.assertEqual(MP3.objects.num_api_calls(), 0)
        self.__success()
        self.assertEqual(MP3.objects.num_api_calls(), 1)

    def test_success_hit(self):
        """
        Ensure that if a local copy of the requested MP3 is present, we can use that without requesting an external server and serialize the data in a response.
        """
        self.assertEqual(MP3.objects.num_api_calls(), 0)
        self.client.get(self.url_path, format='json')
        self.assertEqual(MP3.objects.num_api_calls(), 1)
        self.__success()
        self.assertEqual(MP3.objects.num_api_calls(), 1)

    def test_forbidden(self):
        """
        When querying the external media servers with an invalid ID, we expect an HTTP 403 FORBIDDEN response, which should be interpretted as HTTP 404 NOT FOUND on our end. Ensure that our API provides the appropriate status code
        """
        self.test_id = 'asdsckjn'
        self.url_path = f'/api/{settings.VERSION}/audio/{self.test_id}.mp3'

        self.assertEqual(MP3.objects.num_api_calls(), 0)
        response = self.client.get(self.url_path, format='json')
        self.assertEqual(MP3.objects.num_api_calls(), 1)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        values = {
            NON_FIELD_ERRORS_KEY:
            [ErrorDetail('The specified ID was invalid.', 'not_found')]
        }
        self.assertDictValues(response.data, values)
