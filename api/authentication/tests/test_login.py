import json

from django.conf import settings
from django.urls import reverse

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
        check(f'/api/{settings.VERSION}/auth/login')
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

            for key in {'username', 'email', 'password'}:
                self.assertIn('max_length', POST[key])

            self.assertIn('min_length', POST['password'])

        self.check_urls(check)

    def test_blank_input_with_username(self):
        """
        Ensure that a the proper error messages are sent on blank input. This test uses a blank username field.
        """
        body = {
            'username': '',
            'password': '',
        }

        def check(url):
            response = self.client.post(url, body, format='json')

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            response.data['password'], ['This field may not be blank.']

        self.check_urls(check)

    def test_blank_input_with_email(self):
        """
        Ensure that a the proper error messages are sent on blank input. This test uses a blank email address field.
        """
        body = {
            'email': '',
            'password': '',
        }

        def check(url):
            response = self.client.post(url, body, format='json')

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            self.assertIn(
                'This field may not be blank.', response.data['password'])

        self.check_urls(check)

    def test_missing_input(self):
        """
        Ensure that a the proper error messages are sent on missing input.
        """
        body = {}

        def check(url):
            response = self.client.post(url, body, format='json')

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            self.assertIn(
                'This field is required.', response.data['password'])

        self.check_urls(check)

    def test_partial_input(self):
        """
        Ensure that a the proper error messages are sent on partial input.
        """
        bodies = [
            {
                'username': 'alice',
            },
            {
                'email': 'alice@example.com',
            },
            {
                'password': 'easypass123'
            },
        ]

        def check(url):
            for body in bodies:
                response = self.client.post(url, body, format='json')

                self.assertEqual(
                    response.status_code, status.HTTP_400_BAD_REQUEST)

                if 'password' in body:
                    self.assertIn(
                        'A username or email is required.',
                        response.data['errors'],
                    )
                else:
                    self.assertIn(
                        'The credentials used to login were invalid.',
                        response.data['errors'],
                    )
                    self.assertIn(
                        'This field is required.', response.data['password'])

        self.check_urls(check)

    def test_partial_blank_input(self):
        """
        Ensure that a the proper error messages are sent on partial, but blank, input.
        """
        bodies = [
            {
                'username': ''
            },
            {
                'email': ''
            },
            {
                'password': ''
            },
        ]

        def check(url):
            for body, key in zip(bodies, ['username', 'email', 'password']):
                response = self.client.post(url, body, format='json')

                self.assertEqual(
                    response.status_code, status.HTTP_400_BAD_REQUEST)

                self.assertIn(
                    'The credentials used to login were invalid.',
                    response.data['errors'],
                )

                self.assertIn(
                    'This field may not be blank.',
                    response.data[key],
                )

        self.check_urls(check)

    def test_success_username(self):
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

            self.assertEqual(response.data['username'], 'alice')
            self.assertEqual(response.data['email'], 'alice@example.com')

            tokens = response.data['tokens']
            for key in tokens:
                self.assertRegexpMatches(tokens[key], settings.TOKEN_REGEX)

        self.check_urls(check)

    def test_success_email(self):
        """
        Ensure that we can login successfully with a username and password.
        """
        self.spoof_verification()

        body = {
            'email': 'alice@example.com',
            'password': 'easypass123',
        }

        def check(url):
            response = self.client.post(url, body, format='json')

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            self.assertEqual(response.data['username'], 'alice')
            self.assertEqual(response.data['email'], 'alice@example.com')

            tokens = response.data['tokens']
            for key in tokens:
                self.assertRegexpMatches(tokens[key], settings.TOKEN_REGEX)

        self.check_urls(check)

    def check_invalid_login(self, body, message):
        """
        Method to assist with tests that contain invalid credentials or user data.
        """
        def check(url):
            response = self.client.post(url, body, format='json')

            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            self.assertIn(message, response.data['errors'])

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
