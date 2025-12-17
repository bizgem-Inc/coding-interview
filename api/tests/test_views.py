from rest_framework import status
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        """テスト用のCompanyとCategoryを作成"""
        self.company = Company.objects.create(name="テスト企業")
        self.category = Category.objects.create(
            company=self.company,
            name="テストカテゴリ"
        )

    def test_list(self):
        """カテゴリ一覧の取得テスト"""
        url = "/api/categories/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # ページネーションが設定されている場合は"results"キー、ない場合は直接リスト
        if isinstance(response.data, dict) and "results" in response.data:
            data_list = response.data["results"]
        else:
            data_list = response.data
        self.assertEqual(len(data_list), 1)
        self.assertEqual(data_list[0]["name"], "テストカテゴリ")

    def test_retrieve(self):
        """カテゴリ詳細の取得テスト"""
        url = f"/api/categories/{self.category.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "テストカテゴリ")
        self.assertEqual(str(response.data["company"]), str(self.company.id))

    def test_create(self):
        """カテゴリの作成テスト"""
        url = "/api/categories/"
        data = {
            "company": str(self.company.id),
            "name": "新規カテゴリ"
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "新規カテゴリ")
        self.assertTrue(Category.objects.filter(name="新規カテゴリ").exists())

    def test_update(self):
        """カテゴリの更新テスト"""
        url = f"/api/categories/{self.category.id}/"
        data = {
            "company": str(self.company.id),
            "name": "更新されたカテゴリ"
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "更新されたカテゴリ")
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "更新されたカテゴリ")

    def test_partial_update(self):
        """カテゴリの部分更新テスト"""
        url = f"/api/categories/{self.category.id}/"
        data = {
            "name": "部分更新されたカテゴリ"
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "部分更新されたカテゴリ")
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "部分更新されたカテゴリ")

    def test_destroy(self):
        """カテゴリの削除テスト"""
        url = f"/api/categories/{self.category.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())
