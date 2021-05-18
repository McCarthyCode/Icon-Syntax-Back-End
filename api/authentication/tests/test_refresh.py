import json

from django.conf import settings
from django.urls import reverse

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient, APITestCase

from api.authentication import NON_FIELD_ERRORS_KEY
from api.authentication.models import User

from .mixins import TestCaseShortcutsMixin


class RefreshTests(TestCaseShortcutsMixin, APITestCase):
    """
    Tests to check refresh endpoints. Checks against a hard-coded URL and a reverse-lookup name in nine tests, which check for an OPTIONS request and POST requests that validate user input.
    """
    client = APIClient()
    user = None
    refresh = None
    databases = {'admin_db'}

    def setUp(self):
        """
        Set-up method for constructing the test class. Creates a new User instance and defines the endpoint URL name and path.
        """
        self.user = User.objects.create_user(
            'alice', 'alice@example.com', 'Easypass123!')
        self.spoof_verification()

        self.url_name = 'api:auth:refresh'
        self.url_path = f'/api/{settings.VERSION}/auth/refresh'

    def test_options(self):
        """
        Ensure we can successfully get data from an OPTIONS request.
        """
        response = self.client.options(self.url_path, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        types = {
            'actions': {
                'POST': {
                    'refresh': {
                        'type': str,
                        'required': bool,
                        'read_only': bool,
                        'label': str,
                        'max_length': int
                    },
                    'username': {
                        'type': str,
                        'required': bool,
                        'read_only': bool,
                        'label': str,
                        'max_length': int
                    },
                    'email': {
                        'type': str,
                        'required': bool,
                        'read_only': bool,
                        'label': str,
                        'max_length': int
                    },
                    'password': {
                        'type': str,
                        'required': bool,
                        'read_only': bool,
                        'label': str,
                        'min_length': int,
                        'max_length': int
                    },
                    **self.credentials_types
                }
            },
            **self.options_types
        }
        self.assertDictTypes(response.data, types)

    def test_success_username(self):
        """
        Ensure that we get a successful result on a valid POST request.
        """
        body = {
            'username': 'alice',
            'password': 'Easypass123!',
            'refresh': self.user.refresh
        }

        response = self.client.post(self.url_path, body, format='json')
        self.assertEqual(response.status_code, status.HTTP_303_SEE_OTHER)

        values = {
            'success': 'You have successfully refreshed.',
            'redirect': '/',
            'credentials': None
        }
        self.assertDictValues(response.data, values)
        self.assertCredentialsValid(response.data['credentials'])

    def test_success_email(self):
        """
        Ensure that we get a successful result on a valid POST request.
        """
        body = {
            'email': 'alice@example.com',
            'password': 'Easypass123!',
            'refresh': self.user.refresh
        }

        response = self.client.post(self.url_path, body, format='json')
        self.assertEqual(response.status_code, status.HTTP_303_SEE_OTHER)

        values = {
            'success': 'You have successfully refreshed.',
            'redirect': '/',
            'credentials': None
        }
        self.assertDictValues(response.data, values)
        self.assertCredentialsValid(response.data['credentials'])

    def test_blacklisted_token(self):
        """
        Ensure that we get an unsuccessful response from a request containing a blacklisted token.
        """
        body = {
            'username': 'alice',
            'password': 'Easypass123!',
            'refresh': self.user.refresh
        }

        self.client.post(self.url_path, body, format='json')
        response = self.client.post(self.url_path, body, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        values = {
            NON_FIELD_ERRORS_KEY:
            [ErrorDetail('Token is blacklisted.', 'invalid')]
        }
        self.assertDictValues(response.data, values)

    def test_invalid_token(self):
        """
        Ensure that we get an unsuccessful response from a request containing an invalid token.
        """
        body = {
            'username': 'alice',
            'password': 'Easypass123!',
            'refresh': 'abc123'
        }

        response = self.client.post(self.url_path, body, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        values = {
            NON_FIELD_ERRORS_KEY:
            [ErrorDetail('Token is invalid or expired.', 'invalid')]
        }
        self.assertDictValues(response.data, values)
