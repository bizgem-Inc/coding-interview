from rest_framework.test import APITestCase
from rest_framework import status
from api.models.company import Company
from api.models.category import Category

class CategoryViewTests(APITestCase):

    def setUp(self):
        self.company = Company.objects.create(name="Test Company")
        self.category = Category.objects.create(name="Test Category", company=self.company)
        self.category_data = {
            "name": "New Category",
            "company": self.company.id
        }

    def test_list(self):
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve(self):
        response = self.client.get(f'/api/categories/{self.category.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Category')

    def test_create(self):
        response = self.client.post('/api/categories/', self.category_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], self.category_data['name'])

    def test_update(self):
        updated_data = {"name": "Updated Category"}
        response = self.client.patch(f'/api/categories/{self.category.id}/', updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, updated_data['name'])

    def test_destroy(self):
        response = self.client.delete(f'/api/categories/{self.category.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Category.DoesNotExist):
            Category.objects.get(id=self.category.id)
