from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Company")
        self.parent_category = Category.objects.create(
            company=self.company,
            name="Parent Category",
        )
        self.category = Category.objects.create(
            company=self.company,
            name="Test Category",
            parent_category=self.parent_category,
        )

    def test_list(self):
        url = reverse("category-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve(self):
        url = reverse("category-detail", kwargs={"pk": self.category.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Category")
        self.assertEqual(response.data["company"], self.company.id)
        self.assertEqual(response.data["parent_category"], self.parent_category.id)

    def test_create(self):
        url = reverse("category-list")
        data = {
            "company": str(self.company.id),
            "name": "New Category",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New Category")
        self.assertTrue(Category.objects.filter(name="New Category").exists())

    def test_update(self):
        url = reverse("category-detail", kwargs={"pk": self.category.id})
        data = {
            "company": str(self.company.id),
            "name": "Updated Category",
            "parent_category": None,
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Updated Category")
        self.assertIsNone(self.category.parent_category_id)

    def test_destroy(self):
        url = reverse("category-detail", kwargs={"pk": self.category.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())
