import json

from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient, APITestCase
from api.authentication import NON_FIELD_ERRORS_KEY
from api.authentication.models import User
from api.tests.mixins import TestCaseShortcutsMixin


class RegisterTests(TestCaseShortcutsMixin, APITestCase):
    """
    Tests to check registration endpoints. Checks against a hard-coded URL and a reverse-lookup name in fifteen tests, which check for an OPTIONS request and POST requests that validate user input.
    """
    client = APIClient()

    def setUp(self):
        """
        Set-up method for constructing the test class. Defines the endpoint URL name and path.
        """
        self.url_name = 'api:auth:register'
        self.url_path = f'/api/{settings.VERSION}/auth/register'

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

    def test_blank_input(self):
        """
        Ensure that the proper error messages are sent on blank input.
        """
        body = {
            'username': '',
            'email': '',
            'password': '',
        }

        response = self.client.post(self.url_path, body, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        values = {}
        for key in {'username', 'email', 'password'}:
            values = {
                **values, key:
                [ErrorDetail('This field may not be blank.', 'blank')]
            }
        self.assertDictValues(response.data, values)

    def test_missing_input(self):
        """
        Ensure that the proper error messages are sent on missing input.
        """
        body = {}

        response = self.client.post(self.url_path, body, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        values = {}
        for key in {'username', 'email', 'password'}:
            values = {
                **values, key:
                [ErrorDetail('This field is required.', 'required')]
            }
        self.assertDictValues(response.data, values)

    def test_partial_input(self):
        """
        Ensure that the proper error messages are sent on partial input.
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
            {
                'username': '',
                'email': '',
            },
            {
                'username': '',
                'password': ''
            },
            {
                'email': '',
                'password': ''
            },
        ]

        for body in bodies:
            response = self.client.post(self.url_path, body, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            keys, values = {'username', 'email', 'password'}, {}
            for key in keys:
                in_body = key in body
                values = {
                    **values, key: [
                        ErrorDetail(
                            'This field may not be blank.'
                            if in_body else 'This field is required.',
                            'blank' if in_body else 'required')
                    ]
                }
            self.assertDictValues(response.data, values)

    def test_success(self):
        """
        Ensure we can successfully register a user.
        """
        body = {
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'Easypass123!',
        }

        response = self.client.post(self.url_path, body, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        values = {
            'success':
            _(
                'Step 1 of user registration successful. Check your email for a confirmation link to complete the process.'
            ),
            'credentials':
            None,
        }
        self.assertDictValues(response.data, values)
        self.assertCredentialsValid(
            response.data['credentials'], is_verified=False)

    def test_invalid_email(self):
        """
        Ensure that a user cannot create an account with an invalid email address.
        """
        body = {
            'username': 'alice',
            'email': 'alice',
            'password': 'Easypass123!',
        }

        response = self.client.post(self.url_path, body, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        values = {
            'email': [ErrorDetail('Enter a valid email address.', 'invalid')]
        }
        self.assertDictValues(response.data, values)

    def test_username_exists(self):
        """
        Ensure that a user cannot create an account with an existing username.
        """
        alice, bob = {
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'Easypass123!',
        }, {
            'username': 'alice',
            'email': 'bob@example.com',
            'password': 'Easypass123!',
        }

        self.client.post(self.url_path, alice, format='json')
        response = self.client.post(self.url_path, bob, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        values = {
            'username': [
                ErrorDetail(
                    'A user with this username already exists. Please try again.',
                    'username_exists')
            ]
        }
        self.assertDictValues(response.data, values)

    def test_email_exists(self):
        """
        Ensure that a user cannot create an account with an existing email address.
        """
        alice, bob = {
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'Easypass123!',
        }, {
            'username': 'bob',
            'email': 'alice@example.com',
            'password': 'Easypass123!',
        }

        self.client.post(self.url_path, alice, format='json')
        response = self.client.post(self.url_path, bob, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        values = {
            'email': [
                ErrorDetail(
                    'A user with this email address already exists. Please try again.',
                    'email_exists')
            ]
        }
        self.assertDictValues(response.data, values)

    def test_username_and_email_exist(self):
        """
        Ensure that a user cannot create an account with an existing username and email address.
        """
        body = {
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'Easypass123!',
        }

        self.client.post(self.url_path, body, format='json')
        response = self.client.post(self.url_path, body, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        values = {}
        for key in {'username', 'email'}:
            values = {
                **values, key: [
                    ErrorDetail(
                        f"A user with this {'email address' if key == 'email' else 'username'} already exists. Please try again.",
                        f'{key}_exists')
                ]
            }
        self.assertDictValues(response.data, values)

    def test_password_too_common(self):
        """
        Ensure that a user cannot create an account if the supplied password is too common.
        """
        body = {
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'P@ssw0rd',
        }

        response = self.client.post(self.url_path, body, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        values = {
            NON_FIELD_ERRORS_KEY: [
                ErrorDetail(
                    'This password is too common.', 'password_too_common')
            ]
        }
        self.assertDictValues(response.data, values)

    def test_password_too_short(self):
        """
        Ensure that a user cannot create an account if the supplied password is at least eight characters.
        """
        body = {
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'Abc123!',
        }

        response = self.client.post(self.url_path, body, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        values = {
            'password': [
                ErrorDetail(
                    'Ensure this field has at least 8 characters.',
                    'min_length')
            ]
        }
        self.assertDictValues(response.data, values)

    def test_password_missing_uppercase(self):
        body = {
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'easypass123!',
        }

        response = self.client.post(self.url_path, body)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        values = {
            'password': [
                ErrorDetail(
                    'Your password must contain at least 1 uppercase letter.',
                    'password_missing_upper')
            ]
        }
        self.assertDictValues(response.data, values)

    def test_password_missing_lowercase(self):
        body = {
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'EASYPASS123!',
        }

        response = self.client.post(self.url_path, body)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        values = {
            'password': [
                ErrorDetail(
                    'Your password must contain at least 1 lowercase letter.',
                    'password_missing_lower')
            ]
        }
        self.assertDictValues(response.data, values)

    def test_password_missing_number(self):
        body = {
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'Easypass!',
        }

        response = self.client.post(self.url_path, body)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        values = {
            'password': [
                ErrorDetail(
                    'Your password must contain at least 1 number.',
                    'password_missing_num')
            ]
        }
        self.assertDictValues(response.data, values)

    def test_password_missing_punctuation(self):
        body = {
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'Easypass123',
        }

        response = self.client.post(self.url_path, body)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        values = {
            'password': [
                ErrorDetail(
                    'Your password must contain at least 1 of the following punctuation characters: !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~',
                    'password_missing_punc')
            ]
        }
        self.assertDictValues(response.data, values)

    def check_similar_password(self, body, field_name):
        """
        Helper method used for asserting that similarites between a password and another field are reported in an error message.
        """
        response = self.client.post(self.url_path, body, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        values = {
            NON_FIELD_ERRORS_KEY: [
                ErrorDetail(
                    f'The password is too similar to the {field_name}.',
                    'password_too_similar')
            ]
        }
        self.assertDictValues(response.data, values)

    def test_password_identical_to_username(self):
        """
        Ensure that a user cannot create an account if the supplied password is identical to the supplied username.
        """
        body = {
            'username': 'Harold!23456',
            'email': 'hidethepain@example.com',
            'password': 'Harold!23456',
        }

        self.check_similar_password(body, 'username')

    def test_password_identical_to_email(self):
        """
        Ensure that a user cannot create an account if the supplied password is identical to the supplied email address.
        """
        body = {
            'username': 'isabelle',
            'email': 'Isabelle1@example.com',
            'password': 'Isabelle1@example.com',
        }

        self.check_similar_password(body, 'email address')

    def test_password_similar_to_username(self):
        """
        Ensure that a user cannot create an account if the supplied password is too similar to the supplied username.
        """
        body = {
            'username': 'supercoolusername',
            'email': 'joshua@example.com',
            'password': 'supercoolusername1!AWWYEAH',
        }

        self.check_similar_password(body, 'username')

    def test_password_similar_to_email(self):
        """
        Ensure that a user cannot create an account if the supplied password is too similar to the supplied email address.
        """
        body = {
            'username': 'kelly',
            'email': 'Kelly@example.com',
            'password': 'Kelly@example.com123',
        }

        self.check_similar_password(body, 'email address')
