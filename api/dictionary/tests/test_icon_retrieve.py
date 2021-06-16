import os

from django.conf import settings
from django.urls import reverse

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient, APITestCase

from api import NON_FIELD_ERRORS_KEY
from api.tests.mixins import TestCaseShortcutsMixin
from api.authentication.models import User

from ..models import Icon
from ..utils import ExternalAPIManager


class IconRetrieveTests(TestCaseShortcutsMixin, APITestCase):
    """
    Tests to check search endpoints. Checks against a hard-coded URL and a reverse-lookup name in nine tests, which check for an OPTIONS request and POST requests that validate user input.
    """
    client = APIClient()
    databases = {'default', 'admin_db'}

    url_name = 'api:dict:icon-retrieve'

    def setUp(self):
        """
        Initialization method where a user account is defined and an image is uploaded.
        """
        self.user = User.objects.create_user(
            'alice', 'alice@example.com', 'Easypass123!')

        self.spoof_verification()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user.access}')

        filepath = os.path.join(
            settings.BASE_DIR, 'api/dictionary/tests/media/img/can.GIF')
        with open(filepath, 'rb') as f:
            response = self.client.post(
                reverse('api:dict:icon-upload'), {'icon': f})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        queryset = Icon.objects.all()
        self.assertGreater(len(queryset), 0)
        self.icon = queryset.first()

        self.url_path = \
            f'/api/{settings.VERSION}/icon/{self.icon.id}'
        self.reverse_kwargs = {'id': self.icon.id}

    def test_options(self):
        """
        Ensure we can successfully get data from an OPTIONS request.
        """
        response = self.client.options(self.url_path, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertDictTypes(response.data, self.options_types)

    def test_success(self):
        """
        Ensure we can successfully get data from a GET request.
        """
        icon = Icon.objects.all().first()

        response = self.client.get(self.url_path, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        types = {'id': int, 'icon': str, 'md5': str}
        self.assertDictTypes(response.data, types)

        regexes = {
            'icon':
            r'^(?:[A-Za-z\d+\/]{4})*(?:[A-Za-z\d+\/]{3}=|[A-Za-z\d+\/]{2}==)?$',
            'md5': r'^[a-f\d]{32}$',
        }
        for key, value in regexes.items():
            self.assertRegex(response.data[key], value)

    def test_not_found(self):
        """
        Ensure we can successfully get data from a GET request.
        """
        response = self.client.get(
            f'/api/{settings.VERSION}/icon/999999999', format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        values = {
            NON_FIELD_ERRORS_KEY: [ErrorDetail('Not found.', 'not_found')]
        }
        self.assertEqual(values, response.data)

        # print(response.data)
