from rest_framework.test import APITestCase

from api.models.company import Company
from api.models.category import Category


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Company")
        self.category = Category.objects.create(name="Test Category", company=self.company)

    def test_list(self):
        response = self.client.get(f"/api/companies/{self.company.id}/categories/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], self.category.name)

    def test_retrieve(self):
        response = self.client.get(f"/api/companies/{self.company.id}/categories/{self.category.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], self.category.name)

    def test_create(self):
        response = self.client.post(f"/api/companies/{self.company.id}/categories/", {
            "name": "New Category"
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "New Category")

    def test_update(self):
        response = self.client.put(f"/api/companies/{self.company.id}/categories/{self.category.id}/", {
            "name": "Updated Category"
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Updated Category")

    def test_destroy(self):
        response = self.client.delete(f"/api/companies/{self.company.id}/categories/{self.category.id}/")

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())