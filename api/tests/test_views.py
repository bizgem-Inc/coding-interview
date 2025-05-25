from rest_framework.test import APITestCase
from rest_framework import status
from api.models import Category, Company

class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name='test_company')
        self.parent_category = Category.objects.create(company=self.company, name='parent', parent_category=None)
        self.category = Category.objects.create(company=self.company, name='child', parent_category = self.parent_category)
        self.api_url = '/api/categories/'
        self.api_url_pk = '/api/categories/{}/'

    # 正常系
    def test_list(self):
        response = self.client.get(self.api_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data),2)

    def test_retrieve(self):
        response = self.client.get(self.api_url_pk.format(self.category.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], f'{self.category.id}')
        self.assertEqual(response.data['company']['name'], self.company.name)
        self.assertEqual(response.data['name'], self.category.name)
        self.assertEqual(response.data['parent_category']['name'], self.parent_category.name)

    def test_create(self):
        params = {
            'company': f'{self.company.id}',
            'name': 'created_child',
            'parent_category': f'{self.parent_category.id}',
        }
        response = self.client.post(self.api_url, params, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['company'], self.company.id)
        self.assertEqual(response.data['name'], params['name'])
        self.assertEqual(response.data['parent_category'], self.parent_category.id)

        # DB検証
        category = Category.objects.get(id=response.data['id'])
        self.assertEqual(category.company, self.company)
        self.assertEqual(category.name, params['name'])
        self.assertEqual(category.parent_category, self.parent_category)

    def test_update(self):
        company_for_update = Company.objects.create(name='updated_company')
        category_for_update = Category.objects.create(company=company_for_update, name='updated_category', parent_category=None)
        params = {
            'company': f'{company_for_update.id}',
            'name': 'updated_child',
            'parent_category': f'{category_for_update.id}',
        }
        response = self.client.put(self.api_url_pk.format(self.category.id), params, format='json')
        self.category.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company'], company_for_update.id)
        self.assertEqual(response.data['name'], params['name'])
        self.assertEqual(response.data['parent_category'], category_for_update.id)

        # DB検証
        category = Category.objects.get(id=response.data['id'])
        self.assertEqual(category.company, company_for_update)
        self.assertEqual(category.name, params['name'])
        self.assertEqual(category.parent_category, category_for_update)


    def test_destroy(self):
        response = self.client.delete(self.api_url_pk.format(self.category.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 1)


    # 異常系
    def test_create_empty_name(self):
        params = {
            'company': f'{self.company.id}',
            'name': '',
            'parent_category': f'{self.parent_category.id}',
        }
        response = self.client.post(self.api_url, params, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('This field may not be blank.' in response.data['name'][0])
    
    def test_create_too_long_name(self):
        params = {
            'company': f'{self.company.id}',
            'name': 'A' * 256,
            'parent_category': f'{self.parent_category.id}',
        }
        response = self.client.post(self.api_url, params, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('Ensure this field has no more than' in response.data['name'][0])

    def test_create_empty_company(self):
        params = {
            'company': '',
            'name': 'created_child',
            'parent_category': f'{self.parent_category.id}',
        }
        response = self.client.post(self.api_url, params, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('This field may not be null' in response.data['company'][0])
