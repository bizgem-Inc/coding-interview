from rest_framework import status
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        """Set up test data"""
        self.company = Company.objects.create(name="Test Company")
        self.category1 = Category.objects.create(
            company=self.company,
            name="Category 1"
        )
        self.category2 = Category.objects.create(
            company=self.company,
            name="Category 2",
            parent_category=self.category1
        )

    def test_list(self):
        """Test retrieving list of categories"""
        url = "/api/categories/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve(self):
        """Test retrieving a single category"""
        url = f"/api/categories/{self.category1.id}/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Category 1")
        self.assertEqual(str(response.data["company"]), str(self.company.id))

    def test_create(self):
        """Test creating a new category"""
        url = "/api/categories/"
        data = {
            "company": str(self.company.id),
            "name": "Category 3"
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 3)
        self.assertEqual(response.data["name"], "Category 3")

    def test_update(self):
        """Test updating an existing category"""
        url = f"/api/categories/{self.category1.id}/"
        data = {
            "company": str(self.company.id),
            "name": "Updated Category"
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category1.refresh_from_db()
        self.assertEqual(self.category1.name, "Updated Category")

    def test_destroy(self):
        """Test deleting a category"""
        url = f"/api/categories/{self.category1.id}/"
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 1)
