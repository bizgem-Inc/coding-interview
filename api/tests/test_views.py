from rest_framework.test import APITestCase

from api.models.company import Company
from api.models.category import Category


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Company")
        self.parent_category = Category.objects.create(name="Parent Category", company=self.company)
        self.category = Category.objects.create(name="Test Category", company=self.company, parent_category=self.parent_category)

    def test_list(self):
        response = self.client.get(f"/api/companies/{self.company.id}/categories/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["name"], self.parent_category.name)
        self.assertEqual(response.data[1]["name"], self.category.name)

    def test_retrieve(self):
        response = self.client.get(f"/api/companies/{self.company.id}/categories/{self.category.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], self.category.name)
        self.assertEqual(response.data["parent_category"], self.parent_category.id)

    def test_create_without_parent_category(self):
        response = self.client.post(f"/api/companies/{self.company.id}/categories/", {
            "name": "New Category",
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "New Category")
        self.assertTrue(response.data["parent_category"] is None)

    def test_create_with_parent_category(self):
        response = self.client.post(f"/api/companies/{self.company.id}/categories/", {
            "name": "New Category",
            "parent_category": self.parent_category.id,
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "New Category")
        self.assertEqual(response.data["parent_category"], self.parent_category.id)

    def test_update_without_parent_category(self):
        response = self.client.put(f"/api/companies/{self.company.id}/categories/{self.category.id}/", {
            "name": "Updated Category"
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Updated Category")

    def test_update_with_parent_category(self):
        response = self.client.put(f"/api/companies/{self.company.id}/categories/{self.category.id}/", {
            "name": "Updated Category",
            "parent_category": self.parent_category.id,
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Updated Category")
        self.assertEqual(response.data["parent_category"], self.parent_category.id)

    def test_destroy(self):
        response = self.client.delete(f"/api/companies/{self.company.id}/categories/{self.category.id}/")

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())