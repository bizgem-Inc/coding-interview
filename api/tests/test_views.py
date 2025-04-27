from rest_framework.test import APITestCase, APIClient

from api.factories.category import CategoryFactory
from api.factories.company import CompanyFactory
from api.models.category import Category


class CategoryViewTests(APITestCase):
    client = APIClient()

    def test_list(self):
        category = CategoryFactory(parent_category=None)
        response = self.client.get('/api/category/')
        assert response.status_code == 200
        category_in_response = response.json()[0]

        assert str(category.id) == category_in_response['id']
        assert category.name == category_in_response['name']
        assert category.parent_category == category_in_response['parent_category']
        assert category.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ") == category_in_response['created_at']
        assert category.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ") == category_in_response['updated_at']
        assert str(category.company.id) == category_in_response['company']

    def test_retrieve(self):
        category = CategoryFactory(parent_category=None)
        response = self.client.get(f'/api/category/{str(category.id)}/')
        assert response.status_code == 200
        category_in_response = response.json()

        assert str(category.id) == category_in_response['id']
        assert category.name == category_in_response['name']
        assert category.parent_category == category_in_response['parent_category']
        assert category.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ") == category_in_response['created_at']
        assert category.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ") == category_in_response['updated_at']
        assert str(category.company.id) == category_in_response['company']

    def test_create(self):
        company = CompanyFactory()
        category_json = {
            "company": str(company.id),
            "name": "カテゴリ名",
            "parent_category": None,
        }
        assert Category.objects.count() == 0
        response = self.client.post(f'/api/category/', data=category_json, format='json')
        assert response.status_code == 201
        assert Category.objects.count() == 1

        category = Category.objects.get()
        assert str(category.company.id) == category_json['company']
        assert category.name == category_json['name']
        assert category.parent_category == category_json['parent_category']

    def test_update(self):
        category = CategoryFactory(parent_category=None)
        company = CompanyFactory()
        category_json = {
            "company": str(company.id),
            "name": "カテゴリ名_new",
            "parent_category": None,
        }
        assert Category.objects.count() == 1
        response = self.client.put(f'/api/category/{str(category.id)}/', data=category_json, format='json')
        assert response.status_code == 200
        assert Category.objects.count() == 1

        category = Category.objects.get(id=category.id)
        assert str(category.company.id) == category_json['company']
        assert category.name == category_json['name']
        assert category.parent_category == category_json['parent_category']


    def test_destroy(self):
        category = CategoryFactory(parent_category=None)
        assert Category.objects.count() == 1
        response = self.client.delete(f'/api/category/{str(category.id)}/')
        assert response.status_code == 204
        assert Category.objects.count() == 0
