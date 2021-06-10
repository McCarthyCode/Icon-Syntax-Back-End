import os

from django.conf import settings

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient, APITestCase

from api import NON_FIELD_ERRORS_KEY
from api.test_mixins import TestCaseShortcutsMixin

from ..models import Word, DictionaryEntry
from ..utils import ExternalAPIManager


class IconUploadTests(TestCaseShortcutsMixin, APITestCase):
    """
    Tests to check search endpoints. Checks against a hard-coded URL and a reverse-lookup name in nine tests, which check for an OPTIONS request and POST requests that validate user input.
    """
    client = APIClient()
    databases = {'default', 'admin_db'}

    url_name = 'api:dict:icon-upload'
    url_path = f'/api/{settings.VERSION}/icon/upload'

    def test_options(self):
        """
        Ensure we can successfully get data from an OPTIONS request.
        """
        response = self.client.options(self.url_path, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertDictTypes(response.data, self.options_types)

    def test_empty_request(self):
        """
        Ensure we get an error response on an empty request.
        """
        response = self.client.post(self.url_path)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        values = {
            NON_FIELD_ERRORS_KEY: [
                ErrorDetail(
                    'The request was invalid. Be sure to include an image of maximum width 60 pixels and exact height 54 pixels.',
                    'bad_request')
            ]
        }

    def test_success(self):
        """
        Ensure we can successfully upload an image and get a success response.
        """
        filepath = os.path.join(
            settings.BASE_DIR, 'api/dictionary/tests/media/img/can.GIF')
        with open(filepath, 'rb') as f:
            response = self.client.post(self.url_path, {'icon': f})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        values = {'success': 'File upload successful.'}
        self.assertDictEqual(values, response.data)

    def test_oversized(self):
        """
        Ensure we get an error response when an uploaded image is too large.
        """
        filepath = os.path.join(
            settings.BASE_DIR, 'api/dictionary/tests/media/img/oversized.png')
        with open(filepath, 'rb') as f:
            response = self.client.post(self.url_path, {'icon': f})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        values = {
            NON_FIELD_ERRORS_KEY: [
                ErrorDetail(
                    'The request was invalid. Be sure to include an image of maximum width 60 pixels and exact height 54 pixels.',
                    'bad_request')
            ]
        }
        self.assertDictEqual(values, response.data)
