import json

from django.conf import settings
from django.urls import reverse

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient, APITestCase

from api.authentication import NON_FIELD_ERRORS_KEY
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

            self.assertIn('password', response.data)
            password = response.data['password']

            self.assertIsInstance(password, list)
            self.assertEqual(len(password), 1)

            self.assertIsInstance(password[0], ErrorDetail)
            self.assertEqual('This field may not be blank.', password[0])
            self.assertEqual('blank', password[0].code)

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

            self.assertIn('password', response.data)
            password = response.data['password']

            self.assertIsInstance(password, list)
            self.assertEqual(len(password), 1)

            self.assertIsInstance(password[0], ErrorDetail)
            self.assertEqual('This field may not be blank.', password[0])
            self.assertEqual('blank', password[0].code)

        self.check_urls(check)

    def test_missing_input(self):
        """
        Ensure that a the proper error messages are sent on missing input.
        """
        body = {}

        def check(url):
            response = self.client.post(url, body, format='json')

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            self.assertIn('password', response.data)
            password = response.data['password']

            self.assertIsInstance(password, list)
            self.assertEqual(len(password), 1)

            self.assertIsInstance(password[0], ErrorDetail)
            self.assertEqual('This field is required.', password[0])
            self.assertEqual('required', password[0].code)

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
                    self.assertIn(NON_FIELD_ERRORS_KEY, response.data)
                    errors = response.data[NON_FIELD_ERRORS_KEY]

                    self.assertIsInstance(errors, list)
                    self.assertEqual(len(errors), 1)

                    self.assertIsInstance(errors[0], ErrorDetail)
                    self.assertEqual(
                        'A username or email is required.', errors[0])
                    self.assertEqual('id_required', errors[0].code)
                else:
                    self.assertIn('password', response.data)
                    password = response.data['password']

                    self.assertIsInstance(password, list)
                    self.assertEqual(len(password), 1)

                    self.assertIsInstance(password[0], ErrorDetail)
                    self.assertEqual('This field is required.', password[0])
                    self.assertEqual('required', password[0].code)

        self.check_urls(check)

    def test_partial_blank_input(self):
        """
        Ensure that a the proper error messages are sent on partial, but blank, input.
        """
        def check(url):
            for key in {'username', 'email', 'password'}:
                response = self.client.post(url, {key: ''}, format='json')

                self.assertEqual(
                    response.status_code, status.HTTP_400_BAD_REQUEST)

                self.assertIn(key, response.data)
                field_errors = response.data[key]

                self.assertIsInstance(field_errors, list)
                self.assertEqual(len(field_errors), 1)

                self.assertIsInstance(field_errors[0], ErrorDetail)
                self.assertEqual(
                    'This field may not be blank.', field_errors[0])

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

            self.assertIn('username', response.data)
            username = response.data['username']
            self.assertIsInstance(username, str)
            self.assertEqual(response.data['username'], 'alice')

            self.assertIn('email', response.data)
            email = response.data['email']
            self.assertIsInstance(email, str)
            self.assertEqual(email, 'alice@example.com')

            self.assertIn('tokens', response.data)
            tokens = response.data['tokens']
            self.assertIsInstance(tokens, dict)

            for key, value in tokens.items():
                self.assertIsInstance(value, str)
                self.assertRegexpMatches(value, settings.TOKEN_REGEX)

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

            self.assertIn('username', response.data)
            username = response.data['username']
            self.assertIsInstance(username, str)
            self.assertEqual(response.data['username'], 'alice')

            self.assertIn('email', response.data)
            email = response.data['email']
            self.assertIsInstance(email, str)
            self.assertEqual(email, 'alice@example.com')

            self.assertIn('tokens', response.data)
            tokens = response.data['tokens']
            self.assertIsInstance(tokens, dict)

            for key, value in tokens.items():
                self.assertIsInstance(value, str)
                self.assertRegexpMatches(value, settings.TOKEN_REGEX)

        self.check_urls(check)

    def test_invalid_username(self):
        """
        Ensure that we are denied access with an invalid username.
        """
        body = {
            'username': 'bob',
            'password': 'easypass123',
        }

        def check(url):
            response = self.client.post(url, body, format='json')

            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

            self.assertIn(NON_FIELD_ERRORS_KEY, response.data)
            errors = response.data[NON_FIELD_ERRORS_KEY]

            self.assertIsInstance(errors, list)
            self.assertEqual(len(errors), 1)

            self.assertIsInstance(errors[0], str)
            self.assertEqual(
                'The credentials used to login were invalid.', errors[0])
            self.assertEqual('invalid', errors[0].code)

        self.check_urls(check)

    def test_invalid_password(self):
        """
        Ensure that we are denied access with an invalid password.
        """
        body = {
            'username': 'alice',
            'password': 'whatwasmypasswordagain???',
        }

        def check(url):
            response = self.client.post(url, body, format='json')

            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

            self.assertIn(NON_FIELD_ERRORS_KEY, response.data)
            errors = response.data[NON_FIELD_ERRORS_KEY]

            self.assertIsInstance(errors, list)
            self.assertEqual(len(errors), 1)

            self.assertIsInstance(errors[0], ErrorDetail)
            self.assertEqual(
                'The credentials used to login were invalid.', errors[0])
            self.assertEqual('invalid', errors[0].code)

        self.check_urls(check)

    def test_unverified_email(self):
        """
        Ensure that we are denied access when a verification link has not been followed.
        """
        body = {
            'username': 'alice',
            'password': 'easypass123',
        },

        def check(url):
            response = self.client.post(url, body, format='json')

            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

            self.assertIn(NON_FIELD_ERRORS_KEY, response.data)
            errors = response.data[NON_FIELD_ERRORS_KEY]

            self.assertIsInstance(errors, list)
            self.assertEqual(len(errors), 1)

            self.assertIsInstance(errors[0], ErrorDetail)
            self.assertEqual(
                'Your account has not been verified. Please check your email for a confirmation link.',
                errors[0])
            self.assertEqual('unverified', errors[0].code)

    def test_inactive_user(self):
        """
        Ensure that a deactivated user cannot login, even with the correct credentials.
        """
        self.spoof_verification()
        self.user.is_active = False
        self.user.save()

        body = {
            'username': 'alice',
            'password': 'easypass123',
        },

        def check(url):
            response = self.client.post(url, body, format='json')

            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

            self.assertIn(NON_FIELD_ERRORS_KEY, response.data)
            errors = response.data[NON_FIELD_ERRORS_KEY]

            self.assertIsInstance(errors, list)
            self.assertEqual(len(errors), 1)

            self.assertIsInstance(errors[0], ErrorDetail)
            self.assertEqual(
                'Your account has been temporarily disabled. Please contact the site administrator at webmaster@iconopedia.org.',
                errors[0])
            self.assertEqual('inactive', errors[0].code)

    def test_user_not_found(self):
        """
        Ensure that if a valid token is generated, but the user gets destroyed in the process, the appropriate error message is displayed.
        """
        self.spoof_verification()

        body = {
            'username': 'alice',
            'password': 'easypass123',
        },

        def check(url):
            self.user.delete()
            response = self.client.post(url, body, format='json')

            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

            self.assertIn(NON_FIELD_ERRORS_KEY, response.data)
            errors = response.data[NON_FIELD_ERRORS_KEY]

            self.assertIsInstance(errors, list)
            self.assertEqual(len(errors), 1)

            self.assertIsInstance(errors[0], ErrorDetail)
            self.assertEqual(
                'Your account has been temporarily disabled. Please contact the site administrator at webmaster@iconopedia.org.',
                errors[0])
            self.assertEqual('not_found', errors[0].code)
