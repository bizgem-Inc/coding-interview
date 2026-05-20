import uuid

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

    def test_partial_update(self):
        url = reverse("category-detail", kwargs={"pk": self.category.id})
        response = self.client.patch(url, {"name": "Patched Category"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Patched Category")
        self.assertEqual(self.category.parent_category_id, self.parent_category.id)

    def test_destroy(self):
        url = reverse("category-detail", kwargs={"pk": self.category.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())

    def test_create_duplicate_name_in_same_company_returns_bad_request(self):
        url = reverse("category-list")
        data = {
            "company": str(self.company.id),
            "name": self.category.name,
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_with_unknown_company_returns_bad_request(self):
        url = reverse("category-list")
        data = {
            "company": str(uuid.uuid4()),
            "name": "New Category",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_with_unknown_parent_category_returns_bad_request(self):
        url = reverse("category-list")
        data = {
            "company": str(self.company.id),
            "name": "New Category",
            "parent_category": str(uuid.uuid4()),
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_with_parent_category_from_other_company_returns_bad_request(self):
        other_company = Company.objects.create(name="Other Company")
        other_parent_category = Category.objects.create(
            company=other_company,
            name="Other Parent Category",
        )
        url = reverse("category-list")
        data = {
            "company": str(self.company.id),
            "name": "New Category",
            "parent_category": str(other_parent_category.id),
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_with_self_parent_category_returns_bad_request(self):
        url = reverse("category-detail", kwargs={"pk": self.category.id})
        data = {
            "company": str(self.company.id),
            "name": self.category.name,
            "parent_category": str(self.category.id),
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_with_descendant_parent_category_returns_bad_request(self):
        child_category = Category.objects.create(
            company=self.company,
            name="Child Category",
            parent_category=self.category,
        )
        url = reverse("category-detail", kwargs={"pk": self.category.id})
        data = {
            "company": str(self.company.id),
            "name": self.category.name,
            "parent_category": str(child_category.id),
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
