from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ..models.category import Category
from ..models.company import Company

class CategoryViewTests(APITestCase):
    def setUp(self):
        # テストデータの準備
        self.company = Company.objects.create(name="Test Company")
        
        self.category1 = Category.objects.create(
            company=self.company, 
            name="Electronics"
        )
        self.category2 = Category.objects.create(
            company=self.company, 
            name="Techno"
        )
        
        # URLの定義 (basename='category' と routerで設定されている前提)
        self.list_url = reverse('category-list')

    def _detail_url(self, pk):
        return reverse('category-detail', args=[pk])

    def test_list(self):
        """一覧取得のテスト"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve(self):
        """詳細取得のテスト"""
        url = self._detail_url(self.category1.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Electronics")

    def test_create(self):
        """正常な作成テスト"""
        data = {
            "company": self.company.id, # 認証不要なので明示的に送信する
            "name": "Furniture",
            "parent_category": None
        }
        # null送信のため format='json' が必須
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 3)
        self.assertEqual(Category.objects.get(id=response.data['id']).name, "Furniture")

    def test_create_validation_error_unique(self):
        """異常系: ユニーク制約違反（同一会社・同一カテゴリ名）"""
        data = {
            "company": self.company.id,
            "name": "Electronics", # 既に存在する名前
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # エラーメッセージが含まれているか
        self.assertTrue('non_field_errors' in response.data or 'name' in response.data)

    def test_update(self):
        """正常な更新テスト"""
        url = self._detail_url(self.category1.id)
        data = {
            "company": self.company.id,
            "name": "Consumer Electronics",
            "parent_category": None 
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category1.refresh_from_db()
        self.assertEqual(self.category1.name, "Consumer Electronics")

    def test_update_circular_dependency(self):
        """異常系: 自分自身を親カテゴリに設定しようとした場合"""
        url = self._detail_url(self.category1.id)
        data = {
            "company": self.company.id,
            "name": "Electronics",
            "parent_category": self.category1.id # 自分自身を指定
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('parent_category', response.data)

    def test_destroy(self):
        """削除テスト"""
        url = self._detail_url(self.category1.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 1)