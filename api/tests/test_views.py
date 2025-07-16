from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Category


class CategoryViewTests(APITestCase):
    def setUp(self):
        # URL (Intentionally hardcoded)
        self.list_url = "/api/categories/"

    def test_list_no_date(self):
        """
        The response should be an empty list if no categoy is.
        """

        Category.objects.all().delete()

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 0)

    def test_list(self):
        pass

    def test_retrieve(self):
        pass

    def test_create(self):
        pass

    def test_update(self):
        pass

    def test_destroy(self):
        pass
