from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient, APITestCase

from api.authentication import NON_FIELD_ERRORS_KEY
from api.authentication.models import User
from api.tests.mixins import TestCaseShortcutsMixin


class PasswordForgotVerifyTests(TestCaseShortcutsMixin, APITestCase):
    """
    Tests to ensure that users can get a password reset email when they have forgetten their password.
    """
    client = APIClient

    def setUp(self):
        """
        Set-up method for constructing the test class. Creates a new User instance and defines the endpoint URL name and path.
        """
        self.user = User.objects.create_user(
            'alice', 'alice@example.com', 'Easypass123!')

        self.url_name = 'api:auth:password-forgot-verify'
        self.url_path = f'/api/{settings.VERSION}/auth/password/forgot/verify'

    def test_options(self):
        """
        Ensure we can successfully get data from an unauthenticated OPTIONS request.
        """
        response = self.client.options(self.url_path, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertDictTypes(response.data, self.options_types)

    def test_blank_input(self):
        """
        Ensure that the proper error messages are sent on blank input.
        """
        body = {'password': ''}

        self.spoof_verification()

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user.access}')
        response = self.client.post(self.url_path, body, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        values = {
            'password': [ErrorDetail('This field may not be blank.', 'blank')]
        }
        self.assertDictValues(response.data, values)

    def test_missing_input(self):
        """
        Ensure that the proper error messages are sent on missing input.
        """
        body = {}

        self.spoof_verification()

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user.access}')
        response = self.client.post(self.url_path, body, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        values = {
            'password': [ErrorDetail('This field is required.', 'required')]
        }

        self.assertDictValues(response.data, values)

    def test_success(self):
        """
        Ensure that the user can successfully reset a password, and that the proper credentials are outputted.
        """
        body = {'password': 'Newerpass123!'}

        self.spoof_verification()

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user.access}')
        response = self.client.post(self.url_path, body)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        values = {
            'success': _('Your password has been reset successfully.'),
            'credentials': None,
        }
        self.assertDictValues(response.data, values)
        self.assertCredentialsValid(response.data['credentials'])

        self.user = User.objects.get(pk=self.user.pk)

    def test_unverified(self):
        """
        Ensure that the user cannot reset their password without first verifying their email address.
        """
        body = {
            'password': 'Newerpass123!',
        }

        self.assertFalse(self.user.is_verified)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user.access}')
        response = self.client.post(self.url_path, body)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        values = {
            NON_FIELD_ERRORS_KEY: [
                ErrorDetail(
                    'You do not have permission to perform this action.',
                    'permission_denied')
            ],
        }
        self.assertDictValues(response.data, values)

        self.user = User.objects.get(pk=self.user.pk)

    def test_no_header(self):
        """
        Ensure that the user cannot successfully reset a password if there is no Authorization header.
        """
        body = {'password': 'Easypass123!'}

        self.spoof_verification()

        response = self.client.post(self.url_path, body)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        values = {
            NON_FIELD_ERRORS_KEY: [
                ErrorDetail(
                    'Authentication credentials were not provided.',
                    'not_authenticated')
            ]
        }
        self.assertDictValues(response.data, values)

    def test_new_password_missing_uppercase(self):
        """
        Ensure that the user cannot successfully reset a password if the new password supplied does not contain an uppercase letter.
        """
        body = {'password': 'easypass123!'}

        self.spoof_verification()

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user.access}')
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

    def test_new_password_missing_lowercase(self):
        """
        Ensure that the user cannot successfully reset a password if the new password supplied does not contain a lowercase letter.
        """
        body = {'password': 'EASYPASS123!'}

        self.spoof_verification()

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user.access}')
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

    def test_new_password_missing_number(self):
        """
        Ensure that the user cannot successfully reset a password if the new password supplied does not contain a number.
        """
        body = {'password': 'Easypass!'}

        self.spoof_verification()

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user.access}')
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

    def test_new_password_missing_punctuation(self):
        """
        Ensure that the user cannot successfully reset a password if the new password supplied does not contain a punctuation character.
        """
        body = {'password': 'Easypass123'}

        self.spoof_verification()

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user.access}')
        response = self.client.post(self.url_path, body)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        values = {
            'password': [
                ErrorDetail(
                    'Your password must contain at least 1 of the following punctuation characters: !"#$%&'
                    "'"
                    r'()*+,-./:;<=>?@[\]^_`{|}~', 'password_missing_punc')
            ]
        }
        self.assertDictValues(response.data, values)
