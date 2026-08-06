from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Company")
        self.category = Category.objects.create(company=self.company, name="Category")

    def test_list_returns_categories(self):
        response = self.client.get(reverse("category-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(self.category.id))

    def test_retrieve_returns_category(self):
        response = self.client.get(reverse("category-detail", args=[self.category.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.category.name)

    def test_create_creates_category(self):
        response = self.client.post(
            reverse("category-list"),
            {"company": str(self.company.id), "name": "Created category"},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(name="Created category").exists())

    def test_create_rejects_duplicate_company_and_name(self):
        response = self.client.post(
            reverse("category-list"),
            {"company": str(self.company.id), "name": self.category.name},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Category.objects.count(), 1)

    def test_update_updates_category(self):
        response = self.client.put(
            reverse("category-detail", args=[self.category.id]),
            {"company": str(self.company.id), "name": "Updated category"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Updated category")

    def test_destroy_deletes_category(self):
        response = self.client.delete(reverse("category-detail", args=[self.category.id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())
