import os

from django.conf import settings

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient, APITestCase

from api import NON_FIELD_ERRORS_KEY
from api.tests.mixins import TestCaseShortcutsMixin
from api.authentication.models import User

from ..models import Icon
from ..utils import ExternalAPIManager


class IconUploadTests(TestCaseShortcutsMixin, APITestCase):
    """
    Tests to check search endpoints. Checks against a hard-coded URL and a reverse-lookup name in nine tests, which check for an OPTIONS request and POST requests that validate user input.
    """
    client = APIClient()
    databases = {'default', 'admin_db'}

    url_name = 'api:dict:icon-upload'
    url_path = f'/api/{settings.VERSION}/icon/upload'

    relative_filepath = 'api/dictionary/tests/media/img/can.GIF'

    def setUp(self):
        """
        Initialization method where user accounts are defined.
        """
        self.user = User.objects.create_user(
            'alice', 'alice@example.com', 'Easypass123!')
        self.admin = User.objects.create_superuser(
            'bob', 'bob@example.com', 'Easypass123!')

    def test_options_unauthenticated(self):
        """
        Ensure we can successfully get data from an OPTIONS request.
        """
        response = self.client.options(self.url_path, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        values = {
            NON_FIELD_ERRORS_KEY: [
                ErrorDetail(
                    'Authentication credentials were not provided.',
                    'not_authenticated')
            ]
        }
        self.assertEqual(values, response.data)

    def test_options_authenticated(self):
        """
        Ensure we can successfully get data from an OPTIONS request.
        """
        self.spoof_verification()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user.access}')

        response = self.client.options(self.url_path, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        types = {
            **self.options_types, 'actions': {
                'POST': {
                    'icon': {
                        'type': str,
                        'required': bool,
                        'read_only': bool,
                        'label': str,
                    }
                }
            }
        }
        self.assertDictTypes(response.data, types)

    def test_unauthenticated(self):
        """
        Ensure we get an error response when no authorization header is supplied.
        """
        filepath = os.path.join(settings.BASE_DIR, self.relative_filepath)
        with open(filepath, 'rb') as f:
            response = self.client.post(self.url_path, {'icon': f})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        values = {
            NON_FIELD_ERRORS_KEY: [
                ErrorDetail(
                    'Authentication credentials were not provided.',
                    'not_authenticated')
            ]
        }
        self.assertEqual(values, response.data)

    def test_unverified(self):
        """
        Ensure we get an error response when the user has not verified their email.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user.access}')

        filepath = os.path.join(settings.BASE_DIR, self.relative_filepath)
        with open(filepath, 'rb') as f:
            response = self.client.post(self.url_path, {'icon': f})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        values = {
            NON_FIELD_ERRORS_KEY: [
                ErrorDetail(
                    'You do not have permission to perform this action.',
                    'permission_denied')
            ]
        }
        self.assertEqual(values, response.data)

    def test_empty_request(self):
        """
        Ensure we get an error response on an empty (but authorized) request.
        """
        self.spoof_verification()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user.access}')

        response = self.client.post(self.url_path)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        values = {
            NON_FIELD_ERRORS_KEY: [
                ErrorDetail(
                    'The request was invalid. Be sure to include an image of maximum width 60 pixels and exact height 54 pixels.',
                    'bad_request')
            ]
        }

    def test_success_user(self):
        """
        Ensure we can successfully upload an image and get a success response as a regular user.
        """
        self.spoof_verification()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user.access}')

        filepath = os.path.join(settings.BASE_DIR, self.relative_filepath)
        with open(filepath, 'rb') as f:
            response = self.client.post(self.url_path, {'icon': f})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        values = {'success': 'File upload successful.'}
        self.assertDictEqual(values, response.data)

        self.assertFalse(Icon.objects.all().first().is_approved)

    def test_success_admin(self):
        """
        Ensure we can successfully upload an image and get a success response as an administrator.
        """
        self.spoof_verification()
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.admin.access}')

        filepath = os.path.join(settings.BASE_DIR, self.relative_filepath)
        with open(filepath, 'rb') as f:
            response = self.client.post(self.url_path, {'icon': f})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        values = {'success': 'File upload successful.'}
        self.assertDictEqual(values, response.data)

        self.assertTrue(Icon.objects.all().first().is_approved)

    def test_oversized(self):
        """
        Ensure we get an error response when an uploaded image is too large.
        """
        self.spoof_verification()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user.access}')

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
