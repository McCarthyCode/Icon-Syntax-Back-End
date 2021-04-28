from django.conf import settings
from django.urls import reverse

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient, APITestCase

from api.authentication import NON_FIELD_ERRORS_KEY
from api.authentication.models import User

from .mixins import TestCaseShortcutsMixin


class LogoutTests(TestCaseShortcutsMixin, APITestCase):
    """
    Tests to check logout endpoints. Checks against a hard-coded URL and a reverse-lookup name in nine tests, which check for an OPTIONS request and POST requests that validate user input.
    """
    client = APIClient()
    user = None

    def setUp(self):
        """
        Set-up method for constructing the test class. Creates a new (verified) user.
        """
        self.user = User.objects.create_user(
            'alice', 'alice@example.com', 'Easypass123!')
        self.user.is_verified = True
        self.user.save()

    def check_urls(self, check):
        """
        Method to run test under both URL and URL and reverse-lookup name formats.
        """
        check(f'/api/{settings.VERSION}/auth/logout')
        check(reverse('api:auth:logout'))

    def test_options(self):
        """
        Ensure we can successfully get data from an OPTIONS request.
        """
        def check(url):
            response = self.client.options(url, format='json')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            types = {'actions': {'POST': {}}, **self.options_types}
            self.assertDictTypes(response.data, types)

        self.check_urls(check)

    def test_success(self):
        """
        Ensure that a user can logout successfully.
        """
        body = {'username': 'alice', 'password': 'Easypass123!'}

        def check(url):
            access = self.user.access
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
            response = self.client.post(url)

            self.assertEqual(
                response.status_code, status.HTTP_205_RESET_CONTENT)

            values = {'success': 'You have successfully logged out.'}
            self.assertDictValues(response.data, values)

        self.check_urls(check)

    def test_missing_header(self):
        """
        Ensure that a user cannot logout with a missing header.
        """
        def check(url):
            response = self.client.post(url)

            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

            self.assertIn(NON_FIELD_ERRORS_KEY, response.data)
            errors = response.data[NON_FIELD_ERRORS_KEY]

            self.assertIsInstance(errors, list)
            self.assertEqual(len(errors), 1)

            self.assertIsInstance(errors[0], ErrorDetail)
            self.assertEqual(
                'The authorization token is missing or invalid.', errors[0])
            self.assertEqual('missing_invalid', errors[0].code)

        self.check_urls(check)

    def test_malformed_header(self):
        """
        Ensure that a user cannot logout with a malformed header. This test uses the keyword 'Token' rather than 'Bearer' with a valid access token.
        """
        body = {'username': 'alice', 'password': 'Easypass123!'}

        def check(url):
            access = self.user.access
            self.client.credentials(HTTP_AUTHORIZATION=f'Token {access}')
            response = self.client.post(url)

            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

            self.assertIn(NON_FIELD_ERRORS_KEY, response.data)
            errors = response.data[NON_FIELD_ERRORS_KEY]

            self.assertIsInstance(errors, list)
            self.assertEqual(len(errors), 1)

            self.assertIsInstance(errors[0], ErrorDetail)
            self.assertEqual(
                'The authorization token is missing or invalid.', errors[0])
            self.assertEqual('missing_invalid', errors[0].code)

        self.check_urls(check)

    def test_invalid_token(self):
        """
        Ensure that a user cannot logout with an invalid token.
        """
        def check(url):
            self.client.credentials(HTTP_AUTHORIZATION='Bearer abc123')
            response = self.client.post(url)

            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

            self.assertIn(NON_FIELD_ERRORS_KEY, response.data)
            errors = response.data[NON_FIELD_ERRORS_KEY]

            self.assertIsInstance(errors, list)
            self.assertEqual(len(errors), 1)

            self.assertIsInstance(errors[0], ErrorDetail)
            self.assertEqual(
                'Given token not valid for any token type.', errors[0])
            self.assertEqual('token_not_valid', errors[0].code)

        self.check_urls(check)

    def test_user_gone(self):
        """
        Ensure that a user cannot logout with a token belonging to a user that has been destroyed.
        """
        body = {'username': 'alice', 'password': 'Easypass123!'}

        def check(url):
            access = self.user.access
            self.user.delete()
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
            response = self.client.post(url)

            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

            self.assertIn(NON_FIELD_ERRORS_KEY, response.data)
            errors = response.data[NON_FIELD_ERRORS_KEY]

            self.assertIsInstance(errors, list)
            self.assertEqual(len(errors), 1)

            self.assertIsInstance(errors[0], ErrorDetail)

            self.assertEqual('User not found.', errors[0])
            self.assertEqual('authentication_failed', errors[0].code)

            self.user = User.objects.create_user(
                'alice', 'alice@example.com', 'Easypass123!')

        self.check_urls(check)
