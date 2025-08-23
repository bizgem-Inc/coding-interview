# Author: abe
# Date: 2025-08-23
# Description: Category API tests for coding interview

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from api.models.category import Category
from api.models.company import Company
import uuid


class CategoryViewTests(APITestCase):

    def setUp(self):
        """テストデータのセットアップ"""
        self.company1 = Company.objects.create(name="Test Company 1")
        self.company2 = Company.objects.create(name="Test Company 2")
        
        self.category1 = Category.objects.create(
            company=self.company1,
            name="Electronics"
        )
        self.category2 = Category.objects.create(
            company=self.company1,
            name="Computers",
            parent_category=self.category1
        )
        self.category3 = Category.objects.create(
            company=self.company2,
            name="Books"
        )

    def test_list_categories(self):
        """カテゴリ一覧取得のテスト"""
        url = reverse('category-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        
        # すべてのカテゴリが返されることを確認
        category_names = []
        for cat in response.data:
            category_names.append(cat['name'])
        self.assertIn('Electronics', category_names)
        self.assertIn('Computers', category_names)
        self.assertIn('Books', category_names)

    def test_list_categories_filter_by_company(self):
        """企業によるカテゴリフィルタリングのテスト"""
        url = reverse('category-list')
        response = self.client.get(url, {'company': self.company1.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # company1のカテゴリのみが返されることを確認
        category_names = []
        for cat in response.data:
            category_names.append(cat['name'])
        self.assertIn('Electronics', category_names)
        self.assertIn('Computers', category_names)
        self.assertNotIn('Books', category_names)

    def test_list_categories_filter_by_parent(self):
        """親カテゴリによるフィルタリングのテスト"""
        url = reverse('category-list')
        response = self.client.get(url, {'parent_category': self.category1.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Computers')

    def test_list_categories_filter_by_null_parent(self):
        """親カテゴリなしのフィルタリングのテスト"""
        url = reverse('category-list')
        response = self.client.get(url, {'parent_category': 'null'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        category_names = []
        for cat in response.data:
            category_names.append(cat['name'])
        self.assertIn('Electronics', category_names)
        self.assertIn('Books', category_names)

    def test_retrieve_category(self):
        """カテゴリ詳細取得のテスト"""
        url = reverse('category-detail', args=[self.category1.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Electronics')
        self.assertEqual(response.data['company'], self.company1.id)
        self.assertEqual(response.data['company_name'], 'Test Company 1')
        self.assertIsNone(response.data['parent_category'])

    def test_retrieve_category_with_parent(self):
        """親カテゴリありのカテゴリ詳細取得のテスト"""
        url = reverse('category-detail', args=[self.category2.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Computers')
        self.assertEqual(response.data['parent_category'], self.category1.id)
        self.assertEqual(response.data['parent_category_name'], 'Electronics')

    def test_retrieve_nonexistent_category(self):
        """存在しないカテゴリの詳細取得のテスト"""
        fake_id = uuid.uuid4()
        url = reverse('category-detail', args=[fake_id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_category(self):
        """カテゴリ作成のテスト"""
        url = reverse('category-list')
        data = {
            'company': self.company1.id,
            'name': 'New Category'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Category')
        self.assertEqual(response.data['company'], self.company1.id)
        
        # データベースに実際に作成されたことを確認
        self.assertTrue(Category.objects.filter(name='New Category').exists())

    def test_create_category_with_parent(self):
        """親カテゴリありのカテゴリ作成のテスト"""
        url = reverse('category-list')
        data = {
            'company': self.company1.id,
            'name': 'Sub Category',
            'parent_category': self.category1.id
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Sub Category')
        self.assertEqual(response.data['parent_category'], self.category1.id)
        
        # データベースに実際に作成されたことを確認
        self.assertTrue(Category.objects.filter(name='Sub Category').exists())

    def test_create_category_duplicate_name_same_company(self):
        """同じ企業内での重複名カテゴリ作成のテスト"""
        url = reverse('category-list')
        data = {
            'company': self.company1.id,
            'name': 'Electronics'  # 既に存在
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_category_same_name_different_company(self):
        """異なる企業での同じ名前カテゴリ作成のテスト"""
        url = reverse('category-list')
        data = {
            'company': self.company2.id,
            'name': 'Electronics'  # company1と同じ名前
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Electronics')
        
        # データベースに実際に作成されたことを確認
        self.assertTrue(Category.objects.filter(name='Electronics', company=self.company2).exists())
        
    def test_create_category_parent_different_company(self):
        """異なる企業の親カテゴリでのカテゴリ作成のテスト"""
        url = reverse('category-list')
        data = {
            'company': self.company1.id,
            'name': 'Test Category',
            'parent_category': self.category3.id  # company2から
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_category(self):
        """カテゴリ更新のテスト"""
        url = reverse('category-detail', args=[self.category1.id])
        data = {
            'company': self.company1.id,
            'name': 'Updated Electronics'
        }
        response = self.client.put(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Electronics')
        
        # データベースに実際に更新されたことを確認
        self.category1.refresh_from_db()
        self.assertEqual(self.category1.name, 'Updated Electronics')

    def test_partial_update_category(self):
        """カテゴリ部分更新のテスト"""
        url = reverse('category-detail', args=[self.category1.id])
        data = {'name': 'Partially Updated'}
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Partially Updated')
        # 変更されていないことを確認
        self.assertEqual(response.data['company'], self.company1.id) 
        
        # データベースに実際に更新されたことを確認
        self.category1.refresh_from_db()
        self.assertEqual(self.category1.name, 'Partially Updated')

    def test_update_category_duplicate_name(self):
        """同じ企業内での重複名へのカテゴリ更新のテスト"""
        url = reverse('category-detail', args=[self.category1.id])
        data = {
            'company': self.company1.id,
            'name': 'Computers'  # 既に存在
        }
        response = self.client.put(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_destroy_category(self):
        """カテゴリ削除のテスト"""
        url = reverse('category-detail', args=[self.category3.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # データベースから実際に削除されたことを確認
        self.assertFalse(Category.objects.filter(id=self.category3.id).exists())

    def test_destroy_category_with_children(self):
        """子カテゴリがあるカテゴリの削除のテスト"""
        url = reverse('category-detail', args=[self.category1.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # データベースから削除されていないことを確認
        self.assertTrue(Category.objects.filter(id=self.category1.id).exists())

    def test_destroy_nonexistent_category(self):
        """存在しないカテゴリの削除のテスト"""
        fake_id = uuid.uuid4()
        url = reverse('category-detail', args=[fake_id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


