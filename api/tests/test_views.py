from rest_framework.test import APITestCase
from api.models import Company, Category

class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company1 = Company.objects.create(name="Company1")
        self.company2 = Company.objects.create(name="Company2")
        self.category1 = Category.objects.create(name="Category1", company=self.company1)
        self.category2 = Category.objects.create(name="Category2", company=self.company1)

    def test_list(self):
        response = self.client.get('/api/category/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], "Category1")
        self.assertEqual(response.data[1]['name'], "Category2")

    def test_retrieve(self):
        response = self.client.get(f'/api/category/{self.category1.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], "Category1")

    def test_retrieve_notfound_error(self):
        response = self.client.get(f'/api/category/0/')
        self.assertEqual(response.status_code, 404)

    def test_create(self):
        valid_name = 'A' * 255

        data = {'name': valid_name, 'company': self.company1.id}
        response = self.client.post('/api/category/', data)
        self.assertEqual(response.status_code, 201)

        created_id = response.data['id']
        response = self.client.get(f'/api/category/{created_id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], valid_name)
        self.assertEqual(response.data['company'], self.company1.id)

    def test_create_validate_error_name(self):
        invalud_name = 'A' * 256
        data = {'name': invalud_name, 'company': self.company1.id}
        response = self.client.post('/api/category/', data)
        self.assertEqual(response.status_code, 400)

    def test_update(self):
        data = {'name': 'UpdatedCategory', 'company': self.company2.id}
        response = self.client.put(f'/api/category/{self.category1.id}/', data)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f'/api/category/{self.category1.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'UpdatedCategory')
        self.assertEqual(response.data['company'], self.company2.id)

    def test_destroy(self):
        response = self.client.delete(f'/api/category/{self.category1.id}/')
        self.assertEqual(response.status_code, 204)

        response = self.client.get(f'/api/category/{self.category1.id}/')
        self.assertEqual(response.status_code, 404)

