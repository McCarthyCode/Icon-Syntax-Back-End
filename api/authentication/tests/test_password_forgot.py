from django.conf import settings
from django.urls import reverse

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient, APITestCase

from api.authentication import NON_FIELD_ERRORS_KEY
from api.authentication.models import User

from .mixins import TestCaseShortcutsMixin


class PasswordForgotTests(TestCaseShortcutsMixin, APITestCase):
    """
    Tests to ensure that users can get a password reset email when they have forgetten their password.
    """
    client = APIClient

    def setUp(self):
        self.user = User.objects.create_user(
            'alice', settings.TEST_EMAIL_ADDRESS, 'Easypass123!')
        self.user.is_verified = True
        self.user.save()

    def check_urls(self, check):
        """
        Method to run test under both URL and reverse-lookup name formats.
        """
        check(f'/api/{settings.VERSION}/auth/password/forgot')
        check(reverse('api:auth:password-forgot'))

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
                        'email': {
                            'type': str,
                            'required': bool,
                            'read_only': bool,
                            'label': str,
                            'max_length': int
                        }
                    }
                },
                **self.options_types
            }
            self.assertDictTypes(response.data, types)

        self.check_urls(check)

    def check_success_message(self, url, body):
        response = self.client.post(url, body, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        values = {
            'success':
            'If the email provided is valid, a password reset link should appear in your inbox within a few minutes. Please be sure to check your spam folder.'
        }
        self.assertDictValues(response.data, values)

    def test_success(self):
        """
        Ensure we can successfully handle a POST request.
        """
        body = {'email': settings.TEST_EMAIL_ADDRESS}

        def check(url):
            self.check_success_message(url, body)

        self.check_urls(check)

    def test_quiet_failure(self):
        """
        Ensure that a properly formatted email string not in the database gets a success message. This helps prevent user enumeration attacks.
        """
        body = {'email': 'bob@example.com'}

        def check(url):
            self.check_success_message(url, body)

        self.check_urls(check)

    def test_invalid_email(self):
        """
        Ensure we can send an error message when the email text is not in the right format.
        """
        body = {'email': 'Email? What\'s an email?'}

        def check(url):
            response = self.client.post(url, body, format='json')

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            values = {
                'email':
                [ErrorDetail('Enter a valid email address.', 'invalid')]
            }
            self.assertDictValues(response.data, values)

        self.check_urls(check)
