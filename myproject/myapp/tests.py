from django.test import TestCase
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient
from .models. category import Category ,Company

class CategoryAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.company = Company.objects.create(name='Company Name')  # Companyインスタンスを作成

    # 作成
    def test_create_category(self):
        url = reverse('category-list')  # モデルViewSetのURLを取得
        data = {
            'name': 'Test Category',
            'company': str(self.company.id),  # CompanyインスタンスのIDを文字列として渡す
            'parent_category': None,  # 親カテゴリIDを設定（オプション）
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    # 取得
    def test_get_category_list(self):
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    # 更新
    def test_update_category(self):
        category = Category.objects.create(name='Update Category', company=self.company)
        url = reverse('category-detail', args=[category.id])
        updated_data = {
            'name': 'Updated Category',
        }
        response = self.client.patch(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    # 削除
    def test_delete_category(self):
        category = Category.objects.create(name='Category to Delete', company=self.company)
        url = reverse('category-detail', args=[category.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
