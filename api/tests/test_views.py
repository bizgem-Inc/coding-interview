from rest_framework.test import APITestCase
from rest_framework import status
from ..models.category import Category
from ..models.company import Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Company")

        self.category1 = Category.objects.create(company=self.company, name="Category 1")
        self.category2 = Category.objects.create(company=self.company, name="Category 2")

    def test_list(self):
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve(self):
        response = self.client.get(f'/api/categories/{self.category1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.category1.name)

    def test_create(self):
        data = {
            "company": self.company.id,
            "name": "Category 3",
        }
        response = self.client.post('/api/categories/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 3)

    def test_update(self):
        data = {
            "company": self.company.id,
            "name": "Updated Category 1",
        }
        response = self.client.put(f'/api/categories/{self.category1.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category1.refresh_from_db()
        self.assertEqual(self.category1.name, "Updated Category 1")

    def test_destroy(self):
        response = self.client.delete(f'/api/categories/{self.category1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 1)
