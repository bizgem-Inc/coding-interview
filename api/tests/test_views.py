from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Category
from api.models import Company

import logging


class CategoryViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.Company1 = Company.objects.create(
            name = "Test Company1"
        )
        cls.Category1 = Category.objects.create(
            name = "Test Category1",
            company = cls.Company1,
            parent_category = None
        )
    def test_list(self):
        """
        カテゴリ一覧
        """
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'ステータスコードは200必要')
        self.assertEqual(len(response.data), 1, 'カテゴリ数は1必要')
        self.assertEqual(set(catrgory['name'] for catrgory in response.data), {'Test Category1'}, 'カテゴリ名は「Test Category1」必要')

    def test_retrieve(self):
        """
        カテゴリ詳細
        """
        url = reverse('category-detail', kwargs={'id': self.Category1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'ステータスコードは200必要')
        self.assertEqual(response.data.get('name'), 'Test Category1', 'カテゴリ名は「Test Category1」必要')

    def test_create(self):
        """
        カテゴリ作成
        """
        url = reverse('category-list')
        #親カテゴリなしのテスト
        data = {
            'name': 'Test Category',
            'company': self.Company1.id,
            'parent_category': None,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, 'ステータスコードは201必要')
        self.assertEqual(Category.objects.count(), 2, 'カテゴリ数は2必要')
        self.assertEqual(Category.objects.last().name, 'Test Category', 'カテゴリ名は「Test Category」必要')
        #親カテゴリありのテスト
        data = {
            'name': 'Test Category 2',
            'company': self.Company1.id,
            'parent_category': self.Category1.id,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, '[親カテゴリありのテスト] ステータスコードは201必要')
        self.assertEqual(Category.objects.count(), 3, '[親カテゴリありのテスト] カテゴリ数は2必要')
        self.assertEqual(Category.objects.last().name, 'Test Category 2', '[親カテゴリありのテスト] カテゴリ名は「Test Category 2」必要')
        self.assertEqual(Category.objects.last().parent_category.id, self.Category1.id, '[親カテゴリありのテスト] 親カテゴリは「Test Category1」のID必要')

    def test_update(self):
        """
        カテゴリ更新
        """
        url = reverse('category-detail', kwargs={'id': self.Category1.id})
        data = {
            'name': 'Test Category Update',
            'company': self.Company1.id,
            'parent_category': None,
        }
        response = self.client.put(url, data, format='json')
        category = Category.objects.get(id=self.Category1.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'ステータスコードは200必要')
        self.assertEqual(category.name, 'Test Category Update', 'カテゴリ名は「Test Category Update」必要')

    def test_destroy(self):
        """
        カテゴリ削除
        """
        url = reverse('category-detail', kwargs={'id': self.Category1.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, 'ステータスコードは204必要')
        self.assertEqual(Category.objects.count(), 0, 'カテゴリ数は0必要')

