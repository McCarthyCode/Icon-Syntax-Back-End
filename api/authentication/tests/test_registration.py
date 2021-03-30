import json

from collections import OrderedDict

from django.conf import settings
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from api.authentication.models import User

VERSION = settings.VERSION


class RegistrationTests(APITestCase):
    """
    Tests to check registration endpoints. Checks against a hard-coded URL and a URN in eleven tests, which check for an OPTIONS request and POST requests that validate user input.
    """
    client = APIClient()

    def check_urls(self, check):
        """
        Helper function to run each test under both URL and URN formats.
        """

        check(f'/api/{VERSION}/auth/register/')
        User.objects.all().delete()
        check(reverse('api:auth:register'))

    def test_options(self):
        """
        Ensure we can successfully get data from an OPTIONS request.
        """
        options = {
            'name':
            'Register',
            'description':
            "View for taking in a new user's credentials and sending a confirmation email to verify.",
            'renders': ['application/json', 'text/html'],
            'parses': [
                'application/json', 'application/x-www-form-urlencoded',
                'multipart/form-data'
            ],
            'actions': {
                'POST': {
                    'username': {
                        'type': 'string',
                        'required': True,
                        'read_only': False,
                        'label': 'Username',
                        'max_length': 40
                    },
                    'email': {
                        'type': 'email',
                        'required': True,
                        'read_only': False,
                        'label': 'Email address',
                        'max_length': 80
                    },
                    'password': {
                        'type': 'string',
                        'required': True,
                        'read_only': False,
                        'label': 'Password',
                        'min_length': 8
                    }
                }
            }
        }

        def check(url):
            response = self.client.options(url, format='json')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data, options)

        self.check_urls(check)

    def test_success(self):
        """
        Ensure we can successfully register a user.
        """

        body = {
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'easypass123',
        }

        def check(url):
            response = self.client.post(url, body, format='json')

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data['username'], 'alice')
            self.assertEqual(response.data['email'], 'alice@example.com')

        self.check_urls(check)

    def test_username_exists(self):
        """
        Ensure that a user cannot create an account with an existing username.
        """

        body = {
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'easypass123',
        }

        def check(url):
            self.client.post(url, body, format='json')
            response = self.client.post(url, body, format='json')

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(
                'user with this username already exists.',
                response.data['username'])

        self.check_urls(check)

    def test_email_exists(self):
        """
        Ensure that a user cannot create an account with an existing email address.
        """

        body = {
            'username': 'carol',
            'email': 'carol@example.com',
            'password': 'easypass123',
        }

        def check(url):
            self.client.post(url, body, format='json')
            response = self.client.post(url, body, format='json')

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(
                'user with this email address already exists.',
                response.data['email'])

        self.check_urls(check)

    def test_password_too_common(self):
        """
        Ensure that a user cannot create an account if the supplied password is too common.
        """

        body = {
            'username': 'dave',
            'email': 'dave@example.com',
            'password': 'password',
        }

        def check(url):
            response = self.client.post(url, body, format='json')

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                response.data['non_field_errors'],
                ['This password is too common.'])

        self.check_urls(check)

    def test_password_only_numbers(self):
        """
        Ensure that a user cannot create an account if the supplied password is only numbers.
        """

        body = {
            'username': 'erin',
            'email': 'erin@example.com',
            'password': '123456789012345678901234567890',
        }

        def check(url):
            response = self.client.post(url, body, format='json')

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(
                'This password is entirely numeric.',
                response.data['non_field_errors'])

        self.check_urls(check)

    def test_password_too_short(self):
        """
        Ensure that a user cannot create an account if the supplied password is at least eight characters.
        """

        body = {
            'username': 'frank',
            'email': 'frank@example.com',
            'password': 'abc123',
        }

        def check(url):
            response = self.client.post(url, body, format='json')

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(
                'Ensure this field has at least 8 characters.',
                response.data['password'])

        self.check_urls(check)

    def test_password_identical_to_username(self):
        """
        Ensure that a user cannot create an account if the supplied password is identical to the supplied username.
        """

        body = {
            'username': 'gina123456',
            'email': 'gina@example.com',
            'password': 'gina123456',
        }

        def check(url):
            response = self.client.post(url, body, format='json')

            response.data
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(
                'The password is too similar to the username.',
                response.data['non_field_errors'])

        self.check_urls(check)

    def test_password_identical_to_email(self):
        """
        Ensure that a user cannot create an account if the supplied password is identical to the supplied email address.
        """

        body = {
            'username': 'harold',
            'email': 'hidethepain@example.com',
            'password': 'hidethepain@example.com',
        }

        def check(url):
            response = self.client.post(url, body, format='json')

            data = json.loads(json.dumps(response.data))
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                ['The password is too similar to the email address.'],
                data['non_field_errors'])

        self.check_urls(check)

    def test_password_similar_to_username(self):
        """
        Ensure that a user cannot create an account if the supplied password is too similar to the supplied username.
        """

        body = {
            'username': 'supercoolusername',
            'email': 'isabelle@example.com',
            'password': 'supercoolusername1',
        }

        def check(url):
            response = self.client.post(url, body, format='json')

            data = json.loads(json.dumps(response.data))
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(
                'The password is too similar to the username.',
                data['non_field_errors'])

        self.check_urls(check)

    def test_password_similar_to_email(self):
        """
        Ensure that a user cannot create an account if the supplied password is too similar to the supplied email address.
        """

        body = {
            'username': 'joshua',
            'email': 'joshua@example.com',
            'password': 'joshua@example.com123',
        }

        def check(url):
            response = self.client.post(url, body, format='json')

            data = json.loads(json.dumps(response.data))
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                ['The password is too similar to the email address.'],
                data['non_field_errors'])

        self.check_urls(check)
