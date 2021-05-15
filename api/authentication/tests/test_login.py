import json

from django.conf import settings

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient, APITestCase

from api.authentication import NON_FIELD_ERRORS_KEY
from api.authentication.models import User

from .mixins import TestCaseShortcutsMixin


class LoginTests(TestCaseShortcutsMixin, APITestCase):
    """
    Tests to check login endpoints. Checks against a hard-coded URL and a reverse-lookup name in nine tests, which check for an OPTIONS request and POST requests that validate user input.
    """
    client = APIClient()
    user = None
    databases = {'auth_db'}

    def setUp(self):
        """
        Set-up method for constructing the test class. Creates a new User instance and defines the endpoint URL name and path.
        """
        self.user = User.objects.create_user(
            'alice', 'alice@example.com', 'Easypass123!')

        self.url_name = 'api:auth:login'
        self.url_path = f'/api/{settings.VERSION}/auth/login'

    def test_options(self):
        """
        Ensure we can successfully get data from an OPTIONS request.
        """
        response = self.client.options(self.url_path, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        types = {
            'actions': {
                'POST': {
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

    def test_blank_input_with_username(self):
        """
        Ensure that a the proper error messages are sent on blank input. This test uses a blank username field.
        """
        body = {
            'username': '',
            'password': '',
        }

        response = self.client.post(self.url_path, body, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        values = {
            'username': [ErrorDetail('This field may not be blank.', 'blank')],
            'password': [ErrorDetail('This field may not be blank.', 'blank')]
        }
        self.assertDictValues(response.data, values)

    def test_blank_input_with_email(self):
        """
        Ensure that a the proper error messages are sent on blank input. This test uses a blank email address field.
        """
        body = {
            'email': '',
            'password': '',
        }

        response = self.client.post(self.url_path, body, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        values = {
            'email': [ErrorDetail('This field may not be blank.', 'blank')],
            'password': [ErrorDetail('This field may not be blank.', 'blank')]
        }
        self.assertDictValues(response.data, values)

    def test_missing_input(self):
        """
        Ensure that a the proper error messages are sent on missing input.
        """
        response = self.client.post(self.url_path, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        values = {
            'password': [ErrorDetail('This field is required.', 'required')]
        }
        self.assertDictValues(response.data, values)

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
                'password': 'Easypass123!'
            },
        ]

        for body in bodies:
            response = self.client.post(self.url_path, body, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            if 'password' in body:
                values = {
                    NON_FIELD_ERRORS_KEY: [
                        ErrorDetail(
                            'A username or email is required.', 'id_required')
                    ]
                }
                self.assertDictValues(response.data, values)
            else:
                values = {
                    'password':
                    [ErrorDetail('This field is required.', 'required')]
                }
                self.assertDictValues(response.data, values)

    def test_partial_blank_input(self):
        """
        Ensure that a the proper error messages are sent on partial, but blank, input.
        """
        for key in {'username', 'email', 'password'}:
            response = self.client.post(self.url_path, {key: ''}, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            if key == 'password':
                values = {
                    'password':
                    [ErrorDetail('This field may not be blank.', 'blank')]
                }
                self.assertDictValues(response.data, values)
            else:
                values = {
                    key: [ErrorDetail('This field may not be blank.', 'blank')],
                    'password':
                    [ErrorDetail('This field is required.', 'required')]
                }
                self.assertDictValues(response.data, values)

    def test_success_username(self):
        """
        Ensure that we can login successfully with a username and password.
        """
        self.spoof_verification()

        body = {
            'username': 'alice',
            'password': 'Easypass123!',
        }

        response = self.client.post(self.url_path, body, format='json')
        self.assertEqual(response.status_code, status.HTTP_303_SEE_OTHER)

        values = {
            'success': 'You have successfully logged in.',
            'redirect': '/',
            'credentials': None,
        }

        self.assertDictValues(response.data, values)
        self.assertCredentialsValid(response.data['credentials'])

    def test_success_email(self):
        """
        Ensure that we can login successfully with a username and password.
        """
        self.spoof_verification()

        body = {
            'email': 'alice@example.com',
            'password': 'Easypass123!',
        }

        response = self.client.post(self.url_path, body, format='json')
        self.assertEqual(response.status_code, status.HTTP_303_SEE_OTHER)

        values = {
            'success': 'You have successfully logged in.',
            'redirect': '/',
            'credentials': None,
        }

        self.assertDictValues(response.data, values)
        self.assertCredentialsValid(response.data['credentials'])

    def test_invalid_username(self):
        """
        Ensure that we are denied access with an invalid username.
        """
        body = {
            'username': 'bob',
            'password': 'Easypass123!',
        }

        response = self.client.post(self.url_path, body, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        values = {
            NON_FIELD_ERRORS_KEY: [
                ErrorDetail(
                    'The credentials used to login were invalid.', 'invalid')
            ]
        }
        self.assertDictValues(response.data, values)

    def test_invalid_password(self):
        """
        Ensure that we are denied access with an invalid password.
        """
        body = {
            'username': 'alice',
            'password': 'whatwasmypasswordagain???',
        }

        response = self.client.post(self.url_path, body, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        values = {
            NON_FIELD_ERRORS_KEY: [
                ErrorDetail(
                    'The credentials used to login were invalid.', 'invalid')
            ]
        }
        self.assertDictValues(response.data, values)

    def test_unverified_email(self):
        """
        Ensure that we are denied access when a verification link has not been followed.
        """
        body = {
            'username': 'alice',
            'password': 'Easypass123!',
        }

        response = self.client.post(self.url_path, body, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        values = {
            NON_FIELD_ERRORS_KEY: [
                ErrorDetail(
                    'Your account has not been verified. Please check your email for a confirmation link.',
                    'unverified')
            ]
        }
        self.assertDictValues(response.data, values)

    def test_inactive_user(self):
        """
        Ensure that a deactivated user cannot login, even with the correct credentials.
        """
        self.spoof_verification()
        self.user.is_active = False
        self.user.save()

        body = {
            'username': 'alice',
            'password': 'Easypass123!',
        }

        response = self.client.post(self.url_path, body, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        values = {
            NON_FIELD_ERRORS_KEY: [
                ErrorDetail(
                    'Your account has been temporarily disabled. Please contact the site administrator at webmaster@iconopedia.org.',
                    'disabled')
            ]
        }
        self.assertDictValues(response.data, values)

    def test_user_not_found(self):
        """
        Ensure that if a valid token is generated, but the user gets destroyed in the process, the appropriate error message is displayed.
        """
        body = {
            'username': 'bob',
            'password': 'Easypass123!',
        }

        response = self.client.post(self.url_path, body, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        values = {
            NON_FIELD_ERRORS_KEY: [
                ErrorDetail(
                    'The credentials used to login were invalid.', 'invalid')
            ]
        }
        self.assertDictValues(response.data, values)
