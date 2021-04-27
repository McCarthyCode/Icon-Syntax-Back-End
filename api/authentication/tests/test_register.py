import json

from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient, APITestCase
from api.authentication import NON_FIELD_ERRORS_KEY
from api.authentication.models import User

from .mixins import TestCaseShortcutsMixin


class RegisterTests(TestCaseShortcutsMixin, APITestCase):
    """
    Tests to check registration endpoints. Checks against a hard-coded URL and a reverse-lookup name in fifteen tests, which check for an OPTIONS request and POST requests that validate user input.
    """
    client = APIClient()

    def check_urls(self, check):
        """
        Helper method to run each test under both URL and reverse-lookup name formats.
        """
        check(f'/api/{settings.VERSION}/auth/register')
        User.objects.all().delete()
        check(reverse('api:auth:register'))

    def test_options(self):
        """
        Ensure we can successfully get data from an OPTIONS request.
        """
        def check(url):
            response = self.client.options(url, format='json')

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
                    }
                },
                **self.options_types
            }
            self.assertDictTypes(response.data, types)

        self.check_urls(check)

    def test_blank_input(self):
        """
        Ensure that the proper error messages are sent on blank input.
        """
        body = {
            'username': '',
            'email': '',
            'password': '',
        }

        def check(url):
            response = self.client.post(url, body, format='json')

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            for key in {'username', 'email', 'password'}:
                self.assertIn(key, response.data)
                field_errors = response.data[key]

                self.assertIsInstance(field_errors, list)
                self.assertEqual(len(field_errors), 1)
                self.assertIsInstance(field_errors[0], ErrorDetail)
                self.assertEqual(
                    'This field may not be blank.', field_errors[0])

        self.check_urls(check)

    def test_missing_input(self):
        """
        Ensure that the proper error messages are sent on missing input.
        """
        body = {}

        def check(url):
            response = self.client.post(url, body, format='json')

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            for key in {'username', 'email', 'password'}:
                self.assertIn(key, response.data)
                field_errors = response.data[key]

                self.assertIsInstance(field_errors, list)
                self.assertEqual(len(field_errors), 1)
                self.assertIsInstance(field_errors[0], ErrorDetail)
                self.assertEqual('This field is required.', field_errors[0])

        self.check_urls(check)

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

        def check(url):
            for body in bodies:
                response = self.client.post(url, body, format='json')

                self.assertEqual(
                    response.status_code, status.HTTP_400_BAD_REQUEST)

                keys = {'username', 'email', 'password'}
                for key, in_body in zip(keys, (key in body for key in keys)):
                    self.assertIn(key, response.data)
                    field_errors = response.data[key]

                    self.assertIsInstance(field_errors, list)
                    self.assertEqual(len(field_errors), 1)
                    self.assertIsInstance(field_errors[0], ErrorDetail)
                    self.assertEqual(
                        'This field may not be blank.' if in_body else
                        'This field is required.', field_errors[0])

        self.check_urls(check)

    def test_success(self):
        """
        Ensure we can successfully register a user.
        """
        body = {
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'Easypass123!',
        }

        def check(url):
            response = self.client.post(url, body, format='json')

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            values = {
                'success':
                _(
                    'Step 1 of user registration successful. Check your email for a confirmation link to complete the process.'
                ),
                'username':
                'alice',
                'email':
                'alice@example.com',
            }
            self.check_values_in_dict(response.data, values)

        self.check_urls(check)

    def test_username_exists(self):
        """
        Ensure that a user cannot create an account with an existing username.
        """
        body = {
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'Easypass123!',
        }

        def check(url):
            self.client.post(url, body, format='json')
            response = self.client.post(url, body, format='json')

            self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

            self.assertIn('username', response.data)
            field_errors = response.data['username']

            self.assertIsInstance(field_errors, list)
            self.assertEqual(len(field_errors), 1)
            self.assertIsInstance(field_errors[0], ErrorDetail)
            self.assertEqual(
                'A user with this username already exists. Please try again.',
                field_errors[0])

        self.check_urls(check)

    def test_email_exists(self):
        """
        Ensure that a user cannot create an account with an existing email address.
        """
        body = {
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'Easypass123!',
        }

        def check(url):
            self.client.post(url, body, format='json')
            response = self.client.post(url, body, format='json')

            self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

            self.assertIn('email', response.data)
            field_errors = response.data['email']

            self.assertIsInstance(field_errors, list)
            self.assertEqual(len(field_errors), 1)
            self.assertIsInstance(field_errors[0], ErrorDetail)
            self.assertEqual(
                'A user with this email address already exists. Please try again.',
                field_errors[0])

        self.check_urls(check)

    def test_username_and_email_exist(self):
        """
        Ensure that a user cannot create an account with an existing username and email address.
        """
        body = {
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'Easypass123!',
        }

        def check(url):
            self.client.post(url, body, format='json')
            response = self.client.post(url, body, format='json')

            self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

            for key in {'username', 'email'}:
                self.assertIn(key, response.data)
                field_errors = response.data[key]

                self.assertIsInstance(field_errors, list)
                self.assertEqual(len(field_errors), 1)
                self.assertIsInstance(field_errors[0], ErrorDetail)
                self.assertEqual(
                    f"A user with this {'email address' if key == 'email' else 'username'} already exists. Please try again.",
                    field_errors[0])

        self.check_urls(check)

    def test_password_too_common(self):
        """
        Ensure that a user cannot create an account if the supplied password is too common.
        """
        body = {
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'P@ssw0rd',
        }

        def check(url):
            response = self.client.post(url, body, format='json')

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            self.assertIn(NON_FIELD_ERRORS_KEY, response.data)
            errors = response.data[NON_FIELD_ERRORS_KEY]

            self.assertIsInstance(errors, list)
            self.assertEqual(len(errors), 1)
            self.assertIsInstance(errors[0], ErrorDetail)
            self.assertEqual('This password is too common.', errors[0])

        self.check_urls(check)

    def test_password_too_short(self):
        """
        Ensure that a user cannot create an account if the supplied password is at least eight characters.
        """
        body = {
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'Abc123!',
        }

        def check(url):
            response = self.client.post(url, body, format='json')

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            self.assertIn('password', response.data)
            field_errors = response.data['password']

            self.assertIsInstance(field_errors, list)
            self.assertEqual(len(field_errors), 1)
            self.assertIsInstance(field_errors[0], ErrorDetail)
            self.assertEqual(
                'Ensure this field has at least 8 characters.', field_errors[0])

        self.check_urls(check)

    def test_password_missing_uppercase(self):
        body = {
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'easypass123!',
        }

        def check(url):
            response = self.client.post(url, body)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            self.assertIn('password', response.data)
            field_errors = response.data['password']

            self.assertIsInstance(field_errors, list)
            self.assertEqual(len(field_errors), 1)

            self.assertIsInstance(field_errors[0], ErrorDetail)
            self.assertEqual(
                'Your password must contain at least 1 uppercase character.',
                field_errors[0])
            self.assertEqual('password_missing_upper', field_errors[0].code)

        self.check_urls(check)

    def test_password_missing_lowercase(self):
        body = {
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'EASYPASS123!',
        }

        def check(url):
            response = self.client.post(url, body)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            self.assertIn('password', response.data)
            field_errors = response.data['password']

            self.assertIsInstance(field_errors, list)
            self.assertEqual(len(field_errors), 1)

            self.assertIsInstance(field_errors[0], ErrorDetail)
            self.assertEqual(
                'Your password must contain at least 1 lowercase character.',
                field_errors[0])
            self.assertEqual('password_missing_lower', field_errors[0].code)

        self.check_urls(check)

    def test_password_missing_number(self):
        body = {
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'Easypass!',
        }

        def check(url):
            response = self.client.post(url, body)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            self.assertIn('password', response.data)
            field_errors = response.data['password']

            self.assertIsInstance(field_errors, list)
            self.assertEqual(len(field_errors), 1)

            self.assertIsInstance(field_errors[0], ErrorDetail)
            self.assertEqual(
                'Your password must contain at least 1 number.',
                field_errors[0])
            self.assertEqual('password_missing_num', field_errors[0].code)

        self.check_urls(check)

    def test_password_missing_punctuation(self):
        body = {
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'Easypass123',
        }

        def check(url):
            response = self.client.post(url, body)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            self.assertIn('password', response.data)
            field_errors = response.data['password']

            self.assertIsInstance(field_errors, list)
            self.assertEqual(len(field_errors), 1)

            self.assertIsInstance(field_errors[0], ErrorDetail)
            self.assertEqual(
                'Your password must contain at least 1 of the following punctuation characters: !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~',
                field_errors[0])
            self.assertEqual('password_missing_punc', field_errors[0].code)

        self.check_urls(check)

    def check_similar_password(self, url, body, field_name):
        """
        Helper method used for asserting that similarites between a password and another field are reported in an error message.
        """
        response = self.client.post(url, body, format='json')

        response.data
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn(NON_FIELD_ERRORS_KEY, response.data)
        errors = response.data[NON_FIELD_ERRORS_KEY]

        self.assertIsInstance(errors, list)
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], ErrorDetail)
        self.assertEqual(
            f'The password is too similar to the {field_name}.', errors[0])

    def test_password_identical_to_username(self):
        """
        Ensure that a user cannot create an account if the supplied password is identical to the supplied username.
        """
        body = {
            'username': 'Harold!23456',
            'email': 'hidethepain@example.com',
            'password': 'Harold!23456',
        }

        def check(url):
            self.check_similar_password(url, body, 'username')

        self.check_urls(check)

    def test_password_identical_to_email(self):
        """
        Ensure that a user cannot create an account if the supplied password is identical to the supplied email address.
        """
        body = {
            'username': 'isabelle',
            'email': 'Isabelle1@example.com',
            'password': 'Isabelle1@example.com',
        }

        def check(url):
            self.check_similar_password(url, body, 'email address')

        self.check_urls(check)

    def test_password_similar_to_username(self):
        """
        Ensure that a user cannot create an account if the supplied password is too similar to the supplied username.
        """
        body = {
            'username': 'supercoolusername',
            'email': 'joshua@example.com',
            'password': 'supercoolusername1!AWWYEAH',
        }

        def check(url):
            self.check_similar_password(url, body, 'username')

        self.check_urls(check)

    def test_password_similar_to_email(self):
        """
        Ensure that a user cannot create an account if the supplied password is too similar to the supplied email address.
        """
        body = {
            'username': 'kelly',
            'email': 'Kelly@example.com',
            'password': 'Kelly@example.com123',
        }

        def check(url):
            self.check_similar_password(url, body, 'email address')

        self.check_urls(check)