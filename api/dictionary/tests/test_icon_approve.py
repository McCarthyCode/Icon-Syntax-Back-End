import os

from django.conf import settings
from django.urls import reverse

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient, APITestCase

from api import NON_FIELD_ERRORS_KEY
from api.tests.mixins import TestCaseShortcutsMixin
from api.authentication.models import User

from ..models import Icon
from ..utils import ExternalAPIManager


class IconApproveTests(TestCaseShortcutsMixin, APITestCase):
    """
    Tests to check search endpoints. Checks against a hard-coded URL and a reverse-lookup name in nine tests, which check for an OPTIONS request and POST requests that validate user input.
    """
    client = APIClient()
    databases = {'default', 'admin_db'}

    url_name = 'api:dict:icon-approve'
    url_path = f'/api/{settings.VERSION}/icon/1/approve'

    reverse_kwargs = {'id': 1}

    def setUp(self):
        """
        Initialization method where user accounts are defined and an image is uploaded.
        """
        self.user = User.objects.create_user(
            'alice', 'alice@example.com', 'Easypass123!')
        self.admin = User.objects.create_superuser(
            'bob', 'bob@example.com', 'Easypass123!')

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.admin.access}')

        filepath = os.path.join(
            settings.BASE_DIR, 'api/dictionary/tests/media/img/can.GIF')
        with open(filepath, 'rb') as f:
            data = {'icon': f, 'dictEntry': 'hammer:1'}
            response = self.client.post(
                reverse('api:dict:icon-upload'), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(Icon.objects.all()), 0)

        self.client.credentials(HTTP_AUTHORIZATION=None)

    def test_options_unauthenticated(self):
        """
        Ensure we can get an error message from an OPTIONS request without an authorization header.
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

    def test_options_authenticated_user(self):
        """
        Ensure we can successfully get data from an OPTIONS request.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user.access}')
        response = self.client.options(self.url_path, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        values = {
            NON_FIELD_ERRORS_KEY: [
                ErrorDetail(
                    'You do not have permission to perform this action.',
                    'permission_denied')
            ]
        }
        self.assertEqual(values, response.data)

    def test_options_authenticated_admin(self):
        """
        Ensure we can successfully get data from an OPTIONS request.
        """
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.admin.access}')
        response = self.client.options(self.url_path, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        types = {
            **self.options_types, 'actions': {
                'POST': {
                    'id': {
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
        response = self.client.post(self.url_path, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        values = {
            NON_FIELD_ERRORS_KEY: [
                ErrorDetail(
                    'Authentication credentials were not provided.',
                    'not_authenticated')
            ]
        }
        self.assertEqual(values, response.data)

    def test_authenticated_user(self):
        """
        Ensure we get an error response when a regular user's authorization header is supplied.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user.access}')
        response = self.client.post(self.url_path, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        values = {
            NON_FIELD_ERRORS_KEY: [
                ErrorDetail(
                    'You do not have permission to perform this action.',
                    'permission_denied')
            ]
        }
        self.assertEqual(values, response.data)

    def test_success(self):
        """
        Ensure we get a success response when an admin's authorization header is supplied.
        """

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.admin.access}')
        response = self.client.post(
            reverse(self.url_name, kwargs={'id': Icon.objects.first().id}),
            format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertDictEqual({'success': 'Icon approved.'}, response.data)
        self.assertTrue(Icon.objects.all().first().is_approved)
