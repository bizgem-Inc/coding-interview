from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

class CompanyAPITestCase(APITestCase):

    _url = 'companies'

    def test_list(self):
        """
        会社のリストを取得できること
        """
        response = self.client.get(self._url, format='json')
        self.assertListEqual(response.status_code, status.HTTP_200_OK)
