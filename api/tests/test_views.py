from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from api.models import Category, Company
import uuid

class CategoryViewTests(APITestCase):
    def setUp(self):
        """テストデータのセットアップ"""
        # テスト用の企業を作成
        self.company = Company.objects.create(
            name="Test Company",
        )

        # 別の企業も作成
        self.other_company = Company.objects.create(
            name="Other Company",
        )

        # テスト用のカテゴリを作成
        self.category = Category.objects.create(
            company=self.company,
            name="Test Category"
        )

    def test_list(self):
        """カテゴリー一覧取得のテスト"""
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Category')
        self.assertEqual(response.data[0]['company'], str(self.company.id))

    def test_retrieve(self):
        """カテゴリー詳細取得のテスト"""
        url = reverse('category-detail', kwargs={'pk': self.category.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Category')
        self.assertEqual(response.data['company'], str(self.company.id))

    def test_create(self):
        """カテゴリー作成の正常系テスト"""
        url = reverse('category-list')
        data = {
            'company': str(self.company.id),
            'name': 'New Category'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)
        self.assertEqual(response.data['name'], 'New Category')

    def test_update(self):
        """カテゴリー更新の正常系テスト"""
        url = reverse('category-detail', kwargs={'pk': self.category.id})
        data = {
            'company': str(self.company.id),
            'name': 'Updated Category'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Category')

    def test_destroy(self):
        """カテゴリー削除のテスト"""
        url = reverse('category-detail', kwargs={'pk': self.category.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 0)

    def test_uuid_validation(self):
        """UUID形式のバリデーションテスト"""
        url = reverse('category-list')

        # 不正なUUID形式（company）
        data = {
            'company': 'invalid-uuid',
            'name': 'New Category'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('company', response.data)
        self.assertIn('UUID', str(response.data['company']))

        # 不正なUUID形式（parent_category）
        data = {
            'company': str(self.company.id),
            'name': 'New Category',
            'parent_category': 'invalid-uuid'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('parent_category', response.data)
        self.assertIn('UUID', str(response.data['parent_category']))

    def test_required_fields_validation(self):
        """必須フィールドのバリデーションテスト"""
        url = reverse('category-list')

        # companyが未指定
        data = {
            'name': 'New Category'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('company', response.data)
        self.assertIn('この項目は必須です', str(response.data['company']))

        # nameが未指定
        data = {
            'company': str(self.company.id)
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertIn('この項目は必須です', str(response.data['name']))

    def test_name_validation(self):
        """カテゴリ名のバリデーションテスト"""
        url = reverse('category-list')
        base_data = {'company': str(self.company.id)}

        # 空文字列
        data = {**base_data, 'name': ''}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertIn('この項目は必須です', str(response.data['name']))

        # 51文字の名前
        data = {**base_data, 'name': 'a' * 51}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertIn('50文字以下', str(response.data['name']))

        # 正常なケース
        data = {**base_data, 'name': 'New Test Category'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Test Category')

    def test_duplicate_name_validation(self):
        """カテゴリ名の重複バリデーションテスト"""
        url = reverse('category-list')

        # 同じ会社内での重複
        data = {
            'company': str(self.company.id),
            'name': 'Test Category'  
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertIn('同じ会社内で同じ名前のカテゴリは作成できません', str(response.data))

        # 異なる会社では同名を許可
        data = {
            'company': str(self.other_company.id),
            'name': 'Test Category'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_parent_category_validation(self):
        """親カテゴリのバリデーションテスト"""
        url = reverse('category-list')

        # 異なる会社のカテゴリを親に指定
        other_category = Category.objects.create(
            company=self.other_company,
            name="Other Category"
        )
        data = {
            'company': str(self.company.id),
            'name': 'New Category',
            'parent_category': str(other_category.id)
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('parent_category', response.data)
        self.assertIn('親カテゴリは同じ会社のカテゴリのみ指定できます', str(response.data['parent_category']))

        # 循環参照の作成（更新時）
        child = Category.objects.create(
            company=self.company,
            name="Child Category",
            parent_category=self.category
        )
        url = reverse('category-detail', kwargs={'pk': self.category.id})
        data = {
            'company': str(self.company.id),
            'name': 'Updated Category',
            'parent_category': str(child.id)
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('parent_category', response.data)
        self.assertIn('カテゴリの参照が循環しています', str(response.data['parent_category']))
