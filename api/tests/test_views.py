from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from api.models.company import Company
from api.models.category import Category

class CategoryViewTests(APITestCase):
    def setUp(self):
        """テストデータの作成"""
        self.company = Company.objects.create(name="Test Company")
        self.other_company = Company.objects.create(name="Other Company")
        
        self.category = Category.objects.create(
            company=self.company,
            name="Existing Category"
        )
        
        # URL定義
        self.list_url = reverse('category-list')
        self.detail_url = reverse('category-detail', kwargs={'pk': self.category.id})

    def test_list(self):
        """一覧取得が正常に行われることを確認する"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)

    def test_retrieve(self):
        """詳細取得が正常に行われることを確認する"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.category.name)

    def test_create(self):
        """カテゴリ作成が正常に行われることを確認する"""
        data = {
            "company": self.company.id,
            "name": "New Category",
            "parent_category": self.category.id
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)
        self.assertEqual(Category.objects.get(name="New Category").parent_category, self.category)

    def test_create_unique_error(self):
        """カテゴリ名重複エラーが発生することを確認する"""
        data = {
            "company": self.company.id,
            "name": self.category.name
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_company_mismatch_error(self):
        """会社不整合エラーが発生することを確認する"""
        other_cat = Category.objects.create(company=self.other_company, name="Other")
        data = {
            "company": self.company.id,
            "name": "Mismatch Category",
            "parent_category": other_cat.id
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('parent_category', response.data)

    def test_update(self):
        """カテゴリ更新が正常に行われることを確認する"""
        data = {"company": self.company.id, "name": "Updated Name"}
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Updated Name")

    def test_destroy(self):
        """カテゴリ削除が正常に行われることを確認する"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())