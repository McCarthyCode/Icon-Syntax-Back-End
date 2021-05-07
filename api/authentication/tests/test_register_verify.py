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

    def setUp(self):
        self.user = User.objects.create_user(
            'alice', 'alice@example.com', 'Easypass123!')

    def tearDown(self):
        User.objects.all().delete()

    def check_urls(self, check):
        """
        Method to run each test under both URL and reverse-lookup name formats.
        """
        check(f'/api/{settings.VERSION}/auth/register/verify')
        self.tearDown()
        self.setUp()
        check(reverse('api:auth:verify'))

    def test_options_unauthenticated(self):
        """
        Ensure we can successfully get data from an unauthenticated OPTIONS request.
        """
        def check(url):
            response = self.client.options(url, format='json')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertDictTypes(response.data, self.options_types)

    def test_options_authenticated(self):
        """
        Ensure we can successfully get data from an authenticated OPTIONS request.
        """
        def check(url):
            self.client.credentials(
                HTTP_AUTHORIZATION=f'Bearer {self.user.access}')
            response = self.client.options(url, format='json')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            values = {'actions': {'POST': {}}, **self.options_types}
            self.assertDictTypes(response.data, )

    def test_missing_token(self):
        """
        Ensure that the proper error messages are sent when no Authorization header is provided.
        """
        def check(url):
            response = self.client.post(url)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            values = {
                NON_FIELD_ERRORS_KEY: [
                    ErrorDetail(
                        'The activation link was invalid or has expired.',
                        'invalid')
                ]
            }
            self.assertDictValues(response.data, values)

        self.check_urls(check)

    def test_invalid_token(self):
        """
        Ensure that the proper error messages are sent when an incorrect for token is provided (i.e. 'abc123').
        """
        def check(url):
            self.client.credentials(HTTP_AUTHORIZATION='Bearer abc123')
            response = self.client.post(url)

            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

            values = {
                NON_FIELD_ERRORS_KEY: [
                    ErrorDetail(
                        'Given token not valid for any token type.',
                        'token_not_valid')
                ]
            }
            self.assertDictValues(response.data, values)

        self.check_urls(check)

    def test_success(self):
        """
        Ensure we can successfully verify a user.
        """
        def check(url):
            self.assertFalse(self.user.is_verified)
            self.client.credentials(
                HTTP_AUTHORIZATION=f'Bearer {self.user.access}')
            response = self.client.post(url)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            values = {
                'success':
                _(
                    'You have successfully verified your email address and completed the registration process! You may now access the site\'s full features.'
                ),
                'credentials':
                None,
            }
            self.assertDictValues(response.data, values)
            self.assertCredentialsValid(response.data['credentials'])

            self.assertTrue(User.objects.get(username='alice').is_verified)

        self.check_urls(check)