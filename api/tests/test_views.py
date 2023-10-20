import json

from rest_framework.test import APITestCase
from ..models.category import Category
from ..models.company import Company

class CategoryViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        com = Company.objects.create(name="COT01")
        Category.objects.create(name="CAT01", company=com)
    
    def test_list(self):
        response = self.client.get('/api/category/')
        self.assertEqual(200, response.status_code)
        payload = response.json()
        print(payload)
        com = Company.objects.get(name="COT01")
        self.assertEqual(payload[0]["company"]["id"], str(com.id))

#        self.assertEqual([], payload)
               
        pass

    def test_retrieve(self):
#        response = self.client.post('/api/category/',{'company': ''} )
        pass

    def test_create(self):
        pass

    def test_update(self):
        pass

    def test_destroy(self):
        pass

