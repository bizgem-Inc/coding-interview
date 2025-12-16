from rest_framework.test import APITestCase
from django.urls import reverse
from api.models.category import Category
from api.models.company import Company

class CategoryViewTests(APITestCase):
    def setUp(self):
        # Set up a company and some categories for use in the tests
        self.company = Company.objects.create(name="Test Company")
        self.parent_category = Category.objects.create(company=self.company, name="Parent Category")
        self.category = Category.objects.create(company=self.company, name="Child Category", parent_category=self.parent_category)

    def test_list(self):
        # Test that the list endpoint returns categories
        url = reverse("category-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 1)

    def test_retrieve(self):
        # Test that a single category can be retrieved by its ID
        url = reverse("category-detail", args=[str(self.category.id)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], str(self.category.id))

    def test_create(self):
        # Test that a new category can be created
        url = reverse("category-list")
        data = {
            "company": str(self.company.id),
            "name": "New Category",
            "parent_category": str(self.parent_category.id)
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "New Category")

    def test_update(self):
        # Test that an existing category can be updated
        url = reverse("category-detail", args=[str(self.category.id)])
        data = {
            "company": str(self.company.id),
            "name": "Updated Category",
            "parent_category": str(self.parent_category.id)
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Updated Category")

    def test_destroy(self):
        # Test that a category can be deleted
        url = reverse("category-detail", args=[str(self.category.id)])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())
