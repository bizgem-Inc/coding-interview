from rest_framework.test import APITestCase
from rest_framework import status
from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Company")
        self.category_1 = Category.objects.create(name="Category 1", company=self.company)
        self.category_2 = Category.objects.create(name="Category 2", company=self.company)
        self.create_data = {"name": "Category 3", "company": self.company.id}

    def test_list(self):
        response = self.client.get('/api/category/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], "Category 1")
        self.assertEqual(response.data[1]['name'], "Category 2")

    def test_retrieve(self):
        response = self.client.get(f'/api/category/{self.category_1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Category 1")

    def test_create(self):
        response = self.client.post('/api/category/', data=self.create_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 3)
        self.assertEqual(response.data['name'], "Category 3")

    def test_update(self):
        update_data = {"name" : "Updated Category"}
        response = self.client.patch(f'/api/category/{self.category_1.id}/', data=update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category_1.refresh_from_db()
        self.assertEqual(self.category_1.name, "Updated Category")

    def test_destroy(self):
        response = self.client.delete(f'/api/category/{self.category_1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 1)

    def test_create_with_missing_fields(self):
        invalid_data = {"company": self.company.id}
        response = self.client.post('/api/category/', data=invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_not_exist_category(self):
        response = self.client.get('/api/category/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)