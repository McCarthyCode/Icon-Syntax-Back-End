import json

from django.conf import settings
from django.urls import reverse, reverse_lazy

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from api.authentication.models import User


class LogoutTests(APITestCase):
    """
    Tests to check logout endpoints. Checks against a hard-coded URL and a reverse-lookup name in nine tests, which check for an OPTIONS request and POST requests that validate user input.
    """
    client = APIClient()
    user = None

    def setUp(self):
        """
        Set-up method for constructing the test class. Creates a new (verified) user.
        """
        self.user = User.objects.create_user(
            'alice', 'alice@example.com', 'easypass123')
        self.user.is_verified = True
        self.user.save()

    def check_urls(self, check):
        """
        Method to run test under both URL and URL and reverse-lookup name formats.
        """
        check(f'/api/{settings.VERSION}/auth/logout')
        check(reverse('api:auth:logout'))

    def test_success(self):
        """
        Ensure that a user can logout successfully.
        """
        body = {'username': 'alice', 'password': 'easypass123'}

        def check(url):
            response_login = self.client.post(reverse('api:auth:login'), body)

            access = self.user.tokens()["access"]
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
            response_logout = self.client.post(url)

            self.assertEqual(
                response_logout.status_code, status.HTTP_205_RESET_CONTENT)

        self.check_urls(check)

    def test_missing_header(self):
        """
        Ensure that a user cannot logout with a missing header.
        """
        def check(url):
            response = self.client.post(url)

            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.check_urls(check)

    def test_malformed_header(self):
        """
        Ensure that a user cannot logout with a malformed header.
        """
        body = {'username': 'alice', 'password': 'easypass123'}

        def check(url):
            response_login = self.client.post(reverse('api:auth:login'), body)

            access = self.user.tokens()["access"]
            self.client.credentials(HTTP_AUTHORIZATION=f'Token {access}')
            response_logout = self.client.post(url)

            self.assertEqual(
                response_logout.status_code, status.HTTP_401_UNAUTHORIZED)

        self.check_urls(check)

        self.check_urls(check)

    def test_invalid_token(self):
        """
        Ensure that a user cannot logout with an invalid token.
        """
        def check(url):
            self.client.credentials(HTTP_AUTHORIZATION='Bearer abc123')
            response = self.client.post(url)

            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.check_urls(check)
