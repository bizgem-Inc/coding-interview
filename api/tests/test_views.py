import uuid

from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Category, Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        # Dummy Data
        company0 = Company.objects.create(name="com0")

        category0 = Category.objects.create(company=company0, name="cat0", parent_category=None)
        category0_1 = Category.objects.create(company=company0, name="cat0_1", parent_category=category0)

        self.companies = [company0]
        self.categories = [category0, category0_1]

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
        """
        The response should include all the categories
        """

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), len(self.categories))

        ids_in_db = [str(cat.id) for cat in self.categories]
        for cat in response.data:
            self.assertIn(cat["id"], ids_in_db)

    @staticmethod
    def __retrieve_url(pk):
        return f"/api/categories/{pk}/"

    def test_retrieve(self):
        """
        It should be able to retrieve all the element in DB.
        """

        for cat in self.categories:
            url = self.__retrieve_url(cat.id)
            response = self.client.get(url)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["id"], str(cat.id))

    def test_retrieve_non_existent_category(self):
        """
        It should return 404 Error to retrieve non existent category.
        """

        pk = uuid.uuid4()
        url = self.__retrieve_url(pk)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create(self):
        pass

    def test_update(self):
        pass

    def test_destroy(self):
        pass
