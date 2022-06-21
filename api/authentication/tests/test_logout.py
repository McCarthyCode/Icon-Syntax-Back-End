from django.conf import settings
from django.urls import reverse

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient, APITestCase

from api.authentication import NON_FIELD_ERRORS_KEY
from api.authentication.models import User
from api.tests.mixins import TestCaseShortcutsMixin


class LogoutTests(TestCaseShortcutsMixin, APITestCase):
    """
    Tests to check logout endpoints. Checks against a hard-coded URL and a reverse-lookup name in nine tests, which check for an OPTIONS request and POST requests that validate user input.
    """
    client = APIClient()
    user = None

    def setUp(self):
        """
        Set-up method for constructing the test class. Creates a new User instance, marks it as verified, and defines the endpoint URL name and path.
        """
        self.user = User.objects.create_user(
            'alice', 'alice@example.com', 'Easypass123!')
        self.spoof_verification()

        self.url_name = 'api:auth:logout'
        self.url_path = f'/api/{settings.VERSION}/auth/logout'

    def test_options(self):
        """
        Ensure we can successfully get data from an OPTIONS request when the user is not authenticated.
        """
        response = self.client.options(self.url_path, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertDictTypes(response.data, self.options_types)

    def test_options_authenticated(self):
        """
        Ensure we can successfully get data from an OPTIONS request when the user is authenticated.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user.access}')
        response = self.client.options(self.url_path, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        types = {'actions': {'POST': {}}, **self.options_types}
        self.assertDictTypes(response.data, types)

    def test_success(self):
        """
        Ensure that a user can logout successfully.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user.access}')
        response = self.client.post(self.url_path)
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

        values = {'success': 'You have successfully logged out.'}
        self.assertDictValues(response.data, values)

    def test_missing_header(self):
        """
        Ensure that a user cannot logout with a missing header.
        """
        response = self.client.post(self.url_path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        values = {
            NON_FIELD_ERRORS_KEY: [
                ErrorDetail(
                    'Authentication credentials were not provided.',
                    'not_authenticated')
            ]
        }
        self.assertDictValues(response.data, values)

    def test_malformed_header(self):
        """
        Ensure that a user cannot logout with a malformed header. This test uses the keyword 'Token' rather than 'Bearer' with a valid access token.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user.access}')
        response = self.client.post(self.url_path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        values = {
            NON_FIELD_ERRORS_KEY: [
                ErrorDetail(
                    'Authentication credentials were not provided.',
                    'not_authenticated')
            ]
        }
        self.assertDictValues(response.data, values)

    def test_invalid_token(self):
        """
        Ensure that a user cannot logout with an invalid token.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer abc123')
        response = self.client.post(self.url_path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        values = {
            NON_FIELD_ERRORS_KEY: [
                ErrorDetail(
                    'Given token not valid for any token type.',
                    'token_not_valid')
            ]
        }
        self.assertDictValues(response.data, values)

    def test_user_gone(self):
        """
        Ensure that a user cannot logout with a token belonging to a user that has been destroyed.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user.access}')

        self.user.delete()

        response = self.client.post(self.url_path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        values = {
            NON_FIELD_ERRORS_KEY:
            [ErrorDetail('User not found.', 'authentication_failed')]
        }
        self.assertDictValues(response.data, values)

        self.user = User.objects.create_user(
            'alice', 'alice@example.com', 'Easypass123!')
