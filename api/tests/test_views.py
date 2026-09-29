import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Company")
        self.other_company = Company.objects.create(name="Other Company")

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
        self.assertEqual(len(response.json()), 2)

    def test_retrieve(self):
        url = reverse("category-detail", args=[self.category.id])

        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["id"], str(self.category.id))
        self.assertEqual(data["company"], str(self.company.id))
        self.assertEqual(data["name"], self.category.name)
        self.assertEqual(data["parent_category"], str(self.parent_category.id))

    def test_create(self):
        url = reverse("category-list")
        data = {
            "company": str(self.company.id),
            "name": "New Category",
            "parent_category": str(self.parent_category.id),
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        category = Category.objects.get(id=response.json()["id"])

        self.assertEqual(category.company, self.company)
        self.assertEqual(category.name, "New Category")
        self.assertEqual(category.parent_category, self.parent_category)

    def test_update(self):
        url = reverse("category-detail", args=[self.category.id])
        data = {
            "company": str(self.other_company.id),
            "name": "Updated Category",
            "parent_category": None,
        }

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.category.refresh_from_db()

        self.assertEqual(self.category.company, self.other_company)
        self.assertEqual(self.category.name, "Updated Category")
        self.assertIsNone(self.category.parent_category)

    def test_partial_update(self):
        url = reverse("category-detail", args=[self.category.id])
        data = {
            "name": "Patched Category",
        }

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.category.refresh_from_db()

        self.assertEqual(self.category.name, "Patched Category")
        self.assertEqual(self.category.company, self.company)
        self.assertEqual(self.category.parent_category, self.parent_category)

    def test_destroy(self):
        url = reverse("category-detail", args=[self.category.id])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())

    def test_retrieve_not_found(self):
        url = reverse("category-detail", args=[uuid.uuid4()])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_without_name(self):
        url = reverse("category-list")
        data = {
            "company": str(self.company.id),
            "parent_category": None,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.json())

    def test_create_duplicate(self):
        url = reverse("category-list")
        data = {
            "company": str(self.company.id),
            "name": self.category.name,
            "parent_category": None,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Category.objects.filter(company=self.company, name=self.category.name).count(), 1)
