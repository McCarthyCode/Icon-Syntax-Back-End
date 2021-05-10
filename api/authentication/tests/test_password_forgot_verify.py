from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient, APITestCase

from api.authentication import NON_FIELD_ERRORS_KEY
from api.authentication.models import User

from .mixins import TestCaseShortcutsMixin


class PasswordForgotVerifyTests(TestCaseShortcutsMixin, APITestCase):
    """
    Tests to ensure that users can get a password reset email when they have forgetten their password.
    """
    client = APIClient

    def spoof_verification(self):
        self.user.is_verified = True
        self.user.save()

    def setUp(self):
        self.user = User.objects.create_user(
            'alice', 'alice@example.com', 'Easypass123!')

    def tearDown(self):
        self.user.delete()

    def check_urls(self, check):
        """
        Method to run test under both URL and reverse-lookup name formats.
        """
        check(f'/api/{settings.VERSION}/auth/password/forgot/verify')
        self.tearDown()
        self.setUp()
        check(reverse('api:auth:password-forgot-verify'))

    def test_options_unauthenticated(self):
        """
        Ensure we can successfully get data from an unauthenticated OPTIONS request.
        """
        def check(url):
            response = self.client.options(url, format='json')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertDictTypes(response.data, self.options_types)

        self.check_urls(check)

    def test_options_authenticated(self):
        """
        Ensure we can successfully get data from an authenticated OPTIONS request.
        """
        def check(url):
            self.spoof_verification()

            access = self.user.access
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
            response = self.client.options(url, format='json')

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            types = {
                'actions': {
                    'POST': {
                        'oldPassword': {
                            'type': str,
                            'required': bool,
                            'read_only': bool,
                            'label': str,
                            'min_length': int,
                            'max_length': int
                        },
                        'newPassword': {
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

        self.check_urls(check)

    def test_blank_input(self):
        """
        Ensure that the proper error messages are sent on blank input.
        """
        body = {
            'oldPassword': '',
            'newPassword': '',
        }

        def check(url):
            self.spoof_verification()

            access = self.user.access
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
            response = self.client.post(url, body, format='json')

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            values = dict(
                [
                    (
                        key, [
                            ErrorDetail(
                                'This field may not be blank.', 'blank')
                        ] \
                    ) for key in body
                ])
            self.assertDictValues(response.data, values)

        self.check_urls(check)

    def test_missing_input(self):
        """
        Ensure that the proper error messages are sent on missing input.
        """
        body = {}

        def check(url):
            self.spoof_verification()

            access = self.user.access
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
            response = self.client.post(url, body, format='json')

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            values = dict(
                [
                    (
                        key, [
                            ErrorDetail(
                                'This field is required.', 'required')
                        ] \
                    ) for key in {'oldPassword', 'newPassword'}
                ])
            self.assertDictValues(response.data, values)

        self.check_urls(check)

    def test_partial_input(self):
        """
        Ensure that the proper error messages are sent on partial input.
        """
        keys = {'oldPassword', 'newPassword'}
        bodies = [{key: 'Easypass123!'} for key in keys]

        def check(url):
            self.spoof_verification()

            for body in bodies:
                access = self.user.access
                self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
                response = self.client.post(url, body, format='json')

                self.assertEqual(
                    response.status_code, status.HTTP_400_BAD_REQUEST)

                for key in keys.intersection(response.data):
                    values = {
                        key:
                        [ErrorDetail('This field is required.', 'required')]
                    }
                    self.assertDictValues(response.data, values)

        self.check_urls(check)

    def test_success(self):
        """
        Ensure that the user can successfully reset a password, and that the proper credentials are outputted.
        """
        body = {
            'oldPassword': 'Easypass123!',
            'newPassword': 'Newerpass123!',
        }

        def check(url):
            self.spoof_verification()

            self.assertTrue(self.user.check_password(body['oldPassword']))

            access = self.user.access
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
            response = self.client.post(url, body)

            self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

            values = {
                'success': _('Your password has been reset successfully.'),
                'credentials': None,
            }
            self.assertDictValues(response.data, values)
            self.assertCredentialsValid(response.data['credentials'])

            self.user = User.objects.get(pk=self.user.pk)
            self.assertTrue(self.user.check_password(body['newPassword']))

        self.check_urls(check)

    def test_unverified(self):
        """
        Ensure that the user cannot reset their password without first verifying their email address.
        """
        body = {
            'oldPassword': 'Easypass123!',
            'newPassword': 'Newerpass123!',
        }

        def check(url):
            self.assertTrue(self.user.check_password(body['oldPassword']))
            self.assertFalse(self.user.is_verified)

            access = self.user.access
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
            response = self.client.post(url, body)

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
            self.assertTrue(self.user.check_password(body['oldPassword']))

        self.check_urls(check)

    def test_no_header(self):
        """
        Ensure that the user cannot successfully reset a password if there is no Authorization header.
        """
        body = {
            'oldPassword': 'Easypass123!',
            'newPassword': 'Newerpass123!',
        }

        def check(url):
            self.spoof_verification()

            response = self.client.post(url, body)

            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

            values = {
                NON_FIELD_ERRORS_KEY: [
                    ErrorDetail(
                        'Authentication credentials were not provided.',
                        'not_authenticated')
                ]
            }
            self.assertDictValues(response.data, values)

        self.check_urls(check)

    def test_old_password_mismatch(self):
        """
        Ensure that the user cannot successfully reset a password if the old password supplied does not match the user's current password.
        """
        body = {
            'oldPassword': 'wrongpass123',
            'newPassword': 'Newerpass123!',
        }

        def check(url):
            self.spoof_verification()

            self.assertFalse(self.user.check_password(body['oldPassword']))

            access = self.user.access
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
            response = self.client.post(url, body)

            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

            values = {
                NON_FIELD_ERRORS_KEY: [
                    ErrorDetail(
                        'The old password was not correct. If you have forgotten your password, please use the "forgot password" link.',
                        'mismatch')
                ]
            }
            self.assertDictValues(response.data, values)

        self.check_urls(check)

    def test_new_password_missing_uppercase(self):
        """
        Ensure that the user cannot successfully reset a password if the new password supplied does not contain an uppercase letter.
        """
        body = {
            'oldPassword': 'Easypass123!',
            'newPassword': 'easypass123!',
        }

        def check(url):
            self.spoof_verification()

            self.assertTrue(self.user.check_password(body['oldPassword']))

            access = self.user.access
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
            response = self.client.post(url, body)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            values = {
                'newPassword': [
                    ErrorDetail(
                        'Your password must contain at least 1 uppercase letter.',
                        'password_missing_upper')
                ]
            }
            self.assertDictValues(response.data, values)

        self.check_urls(check)

    def test_new_password_missing_lowercase(self):
        """
        Ensure that the user cannot successfully reset a password if the new password supplied does not contain a lowercase letter.
        """
        body = {
            'oldPassword': 'Easypass123!',
            'newPassword': 'EASYPASS123!',
        }

        def check(url):
            self.spoof_verification()

            self.assertTrue(self.user.check_password(body['oldPassword']))

            access = self.user.access
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
            response = self.client.post(url, body)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            values = {
                'newPassword': [
                    ErrorDetail(
                        'Your password must contain at least 1 lowercase letter.',
                        'password_missing_lower')
                ]
            }
            self.assertDictValues(response.data, values)

        self.check_urls(check)

    def test_new_password_missing_number(self):
        """
        Ensure that the user cannot successfully reset a password if the new password supplied does not contain a number.
        """
        body = {
            'oldPassword': 'Easypass123!',
            'newPassword': 'Easypass!',
        }

        def check(url):
            self.spoof_verification()

            self.assertTrue(self.user.check_password(body['oldPassword']))

            access = self.user.access
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
            response = self.client.post(url, body)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            values = {
                'newPassword': [
                    ErrorDetail(
                        'Your password must contain at least 1 number.',
                        'password_missing_num')
                ]
            }
            self.assertDictValues(response.data, values)

        self.check_urls(check)

    def test_new_password_missing_punctuation(self):
        """
        Ensure that the user cannot successfully reset a password if the new password supplied does not contain a punctuation character.
        """
        body = {
            'oldPassword': 'Easypass123!',
            'newPassword': 'Easypass123',
        }

        def check(url):
            self.spoof_verification()

            self.assertTrue(self.user.check_password(body['oldPassword']))

            access = self.user.access
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
            response = self.client.post(url, body)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            values = {
                'newPassword': [
                    ErrorDetail(
                        'Your password must contain at least 1 of the following punctuation characters: !"#$%&'
                        "'"
                        r'()*+,-./:;<=>?@[\]^_`{|}~', 'password_missing_punc')
                ]
            }
            self.assertDictValues(response.data, values)

        self.check_urls(check)