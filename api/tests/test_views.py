from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Category, Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        """セットアップ: テスト用のCompanyとCategoryを作成し、URLを設定"""
        self.company = Company.objects.create(name="test company")
        self.category = Category.objects.create(
            company=self.company, name="TestCategory"
        )
        self.list_url = reverse("category-list")
        self.detail_url = reverse("category-detail", kwargs={"pk": self.category.id})

    def test_list(self):
        """カテゴリのリストを取得するテスト"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve(self):
        """特定のカテゴリを取得するテスト"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.category.name)

    def test_create(self):
        """新しいカテゴリを作成するテスト"""
        data = {"name": "NewCategory", "company": self.company.id}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)

        # 新しく作成されたカテゴリを取得して検証
        created_category = Category.objects.get(name=data["name"])
        self.assertEqual(created_category.name, data["name"])
        self.assertEqual(created_category.company, self.company)

    def test_update(self):
        """既存のカテゴリを更新するテスト"""
        data = {"name": "Updated Category", "company": self.company.id}
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, data["name"])

    def test_destroy(self):
        """カテゴリを削除するテスト"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 0)

    def test_partial_update(self):
        """カテゴリを部分的に更新するテスト"""
        data = {"name": "Partially Updated Category"}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, data["name"])

    def test_invalid_create(self):
        """無効なデータでカテゴリ作成を試みるテスト"""
        data = {"name": ""}  # Invalid data
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_found_retrieve(self):
        """存在しないカテゴリを取得しようとするテスト"""
        response = self.client.get(
            reverse("category-detail", kwargs={"pk": 999})
        )  # Non-existent ID
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_not_found_update(self):
        """存在しないカテゴリを更新しようとするテスト"""
        data = {"name": "Non-existent Update"}
        response = self.client.put(
            reverse("category-detail", kwargs={"pk": 999}), data
        )  # Non-existent ID
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_not_found_destroy(self):
        """存在しないカテゴリを削除しようとするテスト"""
        response = self.client.delete(
            reverse("category-detail", kwargs={"pk": 999})
        )  # Non-existent ID
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
