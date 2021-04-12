from django.conf import settings
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from api.authentication.models import User


class RegisterVerifyTests(APITestCase):
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

            options = response.data

            self.assertIn('name', options)
            self.assertIn('description', options)
            self.assertIn('renders', options)
            self.assertIn('parses', options)

        self.check_urls(check)

    def test_blank_token(self):
        """
        Ensure that the proper error messages are sent when no value for 'access' is provided (i.e. '/api/{version}/auth/register/verify?access').
        """
        def check(url):
            response = self.client.get(url, {'access': ''})

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            self.assertIn(
                'The activation link was invalid.', response.data['errors'])

        self.check_urls(check)

    def test_missing_token(self):
        """
        Ensure that the proper error messages are sent when no value for 'access' is provided (i.e. '/api/{version}/auth/register/verify').
        """
        def check(url):
            response = self.client.get(url)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(
                'The activation link was invalid.', response.data['errors'])

        self.check_urls(check)

    def test_invalid_token(self):
        """
        Ensure that the proper error messages are sent when an incorrect for 'token' is provided (i.e. '/api/{version}/auth/register/verify?access=abc').
        """
        def check(url):
            response = self.client.get(url, {'access': 'abc123'})

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(
                'The activation link was invalid.', response.data['errors'])

        self.check_urls(check)

    def test_success(self):
        """
        Ensure we can successfully verify a user.
        """
        def check(url):
            user = User.objects.create_user(
                'alice', 'alice@example.com', 'easypass123')
            access = user.tokens()['access']

            response = self.client.get(url, {'access': access})

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            self.assertNotIn('password', response.data)
            self.assertNotIn('errors', response.data)

            self.assertIn('success', response.data)
            self.assertIn('username', response.data)
            self.assertIn('email', response.data)
            self.assertIn('tokens', response.data)

            self.assertEqual(
                'You have successfully verified your email address and completed the registration process! You may now access the site\'s full features.',
                response.data['success'])

            tokens = response.data['tokens']

            for key in {'access', 'refresh'}:
                self.assertIn(key, tokens)
                self.assertRegexpMatches(tokens[key], settings.TOKEN_REGEX)

            self.assertEqual(
                User.objects.get(username='alice').is_verified, True)

        self.check_urls(check)