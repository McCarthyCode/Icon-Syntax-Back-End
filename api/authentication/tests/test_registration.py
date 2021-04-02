import json

from django.conf import settings
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from api.authentication.models import User


class RegistrationTests(APITestCase):
    """
    Tests to check registration endpoints. Checks against a hard-coded URL and a reverse-lookup name in fifteen tests, which check for an OPTIONS request and POST requests that validate user input.
    """
    client = APIClient()

    def check_urls(self, check):
        """
        Method to run each test under both URL and reverse-lookup name formats.
        """
        check(f'/api/{settings.VERSION}/auth/register/')
        User.objects.all().delete()
        check(reverse('api:auth:register'))

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

            for key_a in POST:
                keys = {'type', 'required', 'read_only', 'label', 'max_length'}
                for key_b in keys:
                    self.assertIn(key_b, POST[key_a])

            self.assertIn('min_length', POST['password'])

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
                self.assertEqual(
                    response.data[key], ['This field may not be blank.'])

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
                self.assertEqual(
                    response.data[key], ['This field is required.'])

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
                    self.assertEqual(
                        response.data[key], [
                            'This field may not be blank.'
                            if in_body else 'This field is required.'
                        ])

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

            self.assertNotIn('password', response.data)
            self.assertNotIn('non_field_errors', response.data)

            self.assertIn('success', response.data)
            self.assertIn('username', response.data)
            self.assertIn('email', response.data)

            self.assertEqual(
                response.data['success'],
                'Step 1 of user registration successful. Check your email for a confirmation link to complete the process.'
            )
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

            self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
            self.assertEqual(
                response.data['username'],
                'A user with this username already exists.',
            )

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

            self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
            self.assertEqual(
                response.data['email'],
                'A user with this email address already exists.',
            )

        self.check_urls(check)

    def test_username_and_email_exist(self):
        """
        Ensure that a user cannot create an account with an existing username and email address.
        """
        body = {
            'username': 'dave',
            'email': 'dave@example.com',
            'password': 'easypass123',
        }

        def check(url):
            self.client.post(url, body, format='json')
            response = self.client.post(url, body, format='json')

            self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
            self.assertEqual(
                response.data['username'],
                'A user with this username already exists.',
            )
            self.assertEqual(
                response.data['email'],
                'A user with this email address already exists.',
            )

        self.check_urls(check)

    def test_password_too_common(self):
        """
        Ensure that a user cannot create an account if the supplied password is too common.
        """
        body = {
            'username': 'erin',
            'email': 'erin@example.com',
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
            'username': 'frank',
            'email': 'frank@example.com',
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
            'username': 'gina',
            'email': 'gina@example.com',
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
            'username': 'harold123456',
            'email': 'hidethepain@example.com',
            'password': 'harold123456',
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
            'username': 'isabelle',
            'email': 'isabelle@example.com',
            'password': 'isabelle@example.com',
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
            'email': 'joshua@example.com',
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
            'username': 'kelly',
            'email': 'kelly@example.com',
            'password': 'kelly@example.com123',
        }

        def check(url):
            response = self.client.post(url, body, format='json')

            data = json.loads(json.dumps(response.data))
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                ['The password is too similar to the email address.'],
                data['non_field_errors'])

        self.check_urls(check)
