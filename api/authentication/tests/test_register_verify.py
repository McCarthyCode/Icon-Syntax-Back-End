from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient, APITestCase

from api.authentication import NON_FIELD_ERRORS_KEY
from api.authentication.models import User

from .mixins import TestCaseShortcutsMixin


class RegisterVerifyTests(TestCaseShortcutsMixin, APITestCase):
    """
    Tests to check email verification endpoints. Checks against a hard-coded URL and a reverse-lookup name in five tests, which check for an OPTIONS request and POST requests that validate a query string.
    """
    client = APIClient()

    def check_urls(self, check):
        """
        Method to run each test under both URL and reverse-lookup name formats.
        """
        check(f'/api/{settings.VERSION}/auth/register/verify')
        User.objects.all().delete()
        check(reverse('api:auth:verify'))

    def test_options(self):
        """
        Ensure we can successfully get data from an OPTIONS request.
        """
        def check(url):
            response = self.client.options(url, format='json')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertDictTypes(response.data, self.options_types)

        self.check_urls(check)

    def test_blank_token(self):
        """
        Ensure that the proper error messages are sent when no value for 'access' is provided (i.e. '/api/{version}/auth/register/verify?access').
        """
        def check(url):
            response = self.client.get(url, {'access': ''})

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            self.assertIn('access', response.data)
            field_errors = response.data['access']

            self.assertIsInstance(field_errors, list)
            self.assertEqual(len(field_errors), 1)
            self.assertIsInstance(field_errors[0], ErrorDetail)
            self.assertEqual(
                'The activation link was invalid.', field_errors[0])
            self.assertEqual('invalid', field_errors[0].code)

        self.check_urls(check)

    def test_missing_token(self):
        """
        Ensure that the proper error messages are sent when no value for 'access' is provided (i.e. '/api/{version}/auth/register/verify').
        """
        def check(url):
            response = self.client.get(url)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            self.assertIn('access', response.data)
            field_errors = response.data['access']

            self.assertIsInstance(field_errors, list)
            self.assertEqual(len(field_errors), 1)
            self.assertIsInstance(field_errors[0], ErrorDetail)
            self.assertEqual(
                'The activation link was invalid.', field_errors[0])
            self.assertEqual('invalid', field_errors[0].code)

        self.check_urls(check)

    def test_invalid_token(self):
        """
        Ensure that the proper error messages are sent when an incorrect for 'token' is provided (i.e. '/api/{version}/auth/register/verify?access=abc').
        """
        def check(url):
            response = self.client.get(url, {'access': 'abc123'})

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            self.assertIn('access', response.data)
            field_errors = response.data['access']

            self.assertIsInstance(field_errors, list)
            self.assertEqual(len(field_errors), 1)
            self.assertIsInstance(field_errors[0], ErrorDetail)
            self.assertEqual(
                'The activation link was invalid.', field_errors[0])
            self.assertEqual('invalid', field_errors[0].code)

        self.check_urls(check)

    def test_success(self):
        """
        Ensure we can successfully verify a user.
        """
        def check(url):
            user = User.objects.create_user(
                'alice', 'alice@example.com', 'easypass123')

            self.assertFalse(user.is_verified)
            response = self.client.get(url, {'access': user.access})
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            values = {
                'success':
                _(
                    'You have successfully verified your email address and completed the registration process! You may now access the site\'s full features.'
                ),
                'credentials':
                None,
            }
            self.check_values_in_dict(response.data, values)
            self.check_credentials(response.data['credentials'])

            self.assertTrue(User.objects.get(username='alice').is_verified)

        self.check_urls(check)