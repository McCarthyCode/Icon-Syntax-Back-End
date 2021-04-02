import json

from django.conf import settings
from django.urls import reverse, reverse_lazy

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from api.authentication.models import User


class LoginTests(APITestCase):
    """
    Tests to check login endpoints. Checks against a hard-coded URL and a reverse-lookup name in nine tests, which check for an OPTIONS request and POST requests that validate user input.
    """
    client = APIClient()
    user = None

    def setUp(self):
        """
        Set-up method for constructing the test class. Creates a new user.
        """
        self.user = User.objects.create_user(
            'alice', 'alice@example.com', 'easypass123')

    def spoof_verification(self):
        """
        Method to set is_verified field to True, simulating the user receiving a verification email and clicking the link.
        """
        self.user.is_verified = True
        self.user.save()

    def check_urls(self, check):
        """
        Method to run test under both URL and URL and reverse-lookup name formats.
        """
        check(f'/api/{settings.VERSION}/auth/login/')
        check(reverse('api:auth:login'))

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
            self.assertIn('actions', options)
            self.assertIn('POST', options['actions'])

            POST = options['actions']['POST']

            self.assertIn('username', POST)
            self.assertIn('email', POST)
            self.assertIn('password', POST)
            self.assertIn('tokens', POST)

            for key_a in POST:
                for key_b in {'type', 'required', 'read_only', 'label'}:
                    self.assertIn(key_b, POST[key_a])

            for key_a in {'username', 'email', 'password'}:
                self.assertIn('max_length', POST[key_a])

            self.assertIn('min_length', POST['password'])

        self.check_urls(check)

    def test_blank_input(self):
        """
        Ensure that a the proper error messages are sent on blank input.
        """
        body = {
            'username': '',
            'password': '',
        }

        def check(url):
            response = self.client.post(url, body, format='json')

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            for key in {'username', 'password'}:
                self.assertEqual(
                    response.data[key], ['This field may not be blank.'])

        self.check_urls(check)

    def test_missing_input(self):
        """
        Ensure that a the proper error messages are sent on missing input.
        """
        body = {}

        def check(url):
            response = self.client.post(url, body, format='json')

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            for key in {'username', 'password'}:
                self.assertEqual(
                    response.data[key], ['This field is required.'])

        self.check_urls(check)

    def test_partial_input(self):
        """
        Ensure that a the proper error messages are sent on partial input.
        """
        bodies = [{'username': ''}, {'password': ''}]

        def check(url):
            for body in bodies:
                response = self.client.post(url, body, format='json')

                self.assertEqual(
                    response.status_code, status.HTTP_400_BAD_REQUEST)

                keys = {'username', 'password'}
                for key, in_body in zip(keys, (key in body for key in keys)):
                    self.assertEqual(
                        response.data[key], [
                            'This field may not be blank.'
                            if in_body else 'This field is required.'
                        ])

        self.check_urls(check)

    def test_success(self):
        """
        Ensure that we can login successfully with a username and password.
        """
        self.spoof_verification()

        body = {
            'username': 'alice',
            'password': 'easypass123',
        }

        def check(url):
            response = self.client.post(url, body, format='json')

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            tokens = response.data['tokens']
            for key in tokens:
                self.assertRegexpMatches(
                    tokens[key],
                    r'^[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*$')

        self.check_urls(check)

    def check_invalid_login(self, body, message):
        """
        Method to assist with tests that contain invalid credentials or user data.
        """
        def check(url):
            response = self.client.post(url, body, format='json')

            self.assertEqual(
                response.status_code, status.HTTP_401_UNAUTHORIZED)
            self.assertEqual(response.data['error'], message)

        self.check_urls(check)

    def test_invalid_username(self):
        """
        Ensure that we are denied access with an invalid username.
        """
        self.check_invalid_login(
            {
                'username': 'bob',
                'password': 'easypass123',
            }, 'The credentials used to login were invalid.')

    def test_invalid_password(self):
        """
        Ensure that we are denied access with an invalid password.
        """
        self.check_invalid_login(
            {
                'username': 'alice',
                'password': 'whatwasmypasswordagain???',
            }, 'The credentials used to login were invalid.')

    def test_unverified_email(self):
        """
        Ensure that we are denied access when a verification link has not been followed.
        """
        self.check_invalid_login(
            {
                'username': 'alice',
                'password': 'easypass123',
            },
            'Your account has not been verified. Please check your email for a confirmation link.'
        )

    def test_inactive_user(self):
        """
        Ensure that a deactivated user cannot login, even with the correct credentials.
        """
        self.spoof_verification()
        self.user.is_active = False
        self.user.save()

        self.check_invalid_login(
            {
                'username': 'alice',
                'password': 'easypass123',
            },
            'Your account has been temporarily disabled. Please contact the site administrator at webmaster@iconopedia.org.'
        )
