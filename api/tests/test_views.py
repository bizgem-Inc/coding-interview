from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Company")
        self.category = Category.objects.create(company=self.company, name="Test Category")
        self.list_url = reverse("category-list")
        self.detail_url = reverse("category-detail", kwargs={"pk": self.category.pk})

    def test_list(self):
        response = self.client.get(self.list_url, {"company": self.company.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Test Category")

    def test_list_without_company(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Category")

    def test_create(self):
        data = {
            "company": self.company.pk,
            "name": "New Category"
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)
        self.assertEqual(response.data["name"], "New Category")

    def test_update(self):
        data = {
            "company": self.company.pk,
            "name": "Updated Category"
        }
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Updated Category")

    def test_destroy(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 0)
