from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from api.models.company import Company
from api.models.category import Category

class CategoryViewTests(APITestCase):
    def setUp(self):
        # テスト用の企業とカテゴリを作成
        self.company = Company.objects.create(name='Test Company')
        self.other_company = Company.objects.create(name='Other Company')
        self.category = Category.objects.create(company=self.company, name='Test Category')
        self.category_data = {'company': self.company.id, 'name': 'New Category'}
        self.updated_category_data = {'company': self.company.id, 'name': 'Updated Category'}

    def test_list(self):
        """
        カテゴリ一覧取得確認
        """
        url = reverse('category-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve(self):
        """
        カテゴリ詳細取得確認
        """
        url = reverse('category-detail', kwargs={'pk': self.category.id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.category.name)

    def test_create(self):
        """
        カテゴリ新規作成確認
        """
        url = reverse('category-list')
        response = self.client.post(url, self.category_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)
        self.assertEqual(Category.objects.get(id=response.data['id']).name, 'New Category')

    def test_update(self):
        """
        カテゴリ更新確認
        """
        url = reverse('category-detail', kwargs={'pk': self.category.id})
        response = self.client.put(url, self.updated_category_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Updated Category')

    def test_destroy(self):
        """
        カテゴリ削除確認
        """
        url = reverse('category-detail', kwargs={'pk': self.category.id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 0)

    def test_duplicate_category_name_within_same_company(self):
        """
        同一企業内で同じカテゴリ名は作成できないことを確認
        """
        url = reverse('category-list')
        data = {'company': self.company.id, 'name': 'Test Category'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_parent_category_must_belong_to_same_company(self):
        """
        親カテゴリが異なる企業に属している場合はバリデーションエラーになることを確認
        """
        other_category = Category.objects.create(company=self.other_company, name='Other Category')
        url = reverse('category-list')
        data = {
            'company': self.company.id,
            'name': 'Sub Category',
            'parent_category': other_category.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
