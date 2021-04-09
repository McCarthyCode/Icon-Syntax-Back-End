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
