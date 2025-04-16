from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..models.category import Category
from ..models.company import Company


class CategoryViewSetTests(APITestCase):
    """
    カテゴリ管理APIのテストクラス
    CRUD操作の各エンドポイントの動作を検証します
    """

    def setUp(self):
        """
        テストの前準備
        各テストケースで使用するテストデータを作成します
        """
        # テスト用の会社を作成
        self.company = Company.objects.create(name="Test Company")
        # テスト用のカテゴリを作成
        self.category = Category.objects.create(
            company=self.company,
            name="Test Category"
        )
        # テスト用の親カテゴリを作成
        self.parent_category = Category.objects.create(
            company=self.company,
            name="Parent Category"
        )

    def test_list_categories(self):
        """
        カテゴリ一覧取得APIのテスト
        - ステータスコード200が返されること
        - 作成した2つのカテゴリが返されること
        """
        url = reverse("category-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_category(self):
        """
        カテゴリ作成APIのテスト
        - ステータスコード201が返されること
        - カテゴリが正しく作成されること
        - 作成されたカテゴリの名前が正しいこと
        """
        url = reverse("category-list")
        data = {
            "company": self.company.id,
            "name": "New Category",
            "parent_category": self.parent_category.id
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 3)
        self.assertEqual(Category.objects.get(id=response.data["id"]).name, "New Category")

    def test_retrieve_category(self):
        """
        カテゴリ詳細取得APIのテスト
        - ステータスコード200が返されること
        - 取得したカテゴリの名前が正しいこと
        """
        url = reverse("category-detail", args=[self.category.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.category.name)

    def test_update_category(self):
        """
        カテゴリ更新APIのテスト
        - ステータスコード200が返されること
        - カテゴリが正しく更新されること
        - 更新後のカテゴリの名前が正しいこと
        """
        url = reverse("category-detail", args=[self.category.id])
        data = {
            "company": self.company.id,
            "name": "Updated Category",
            "parent_category": self.parent_category.id
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Updated Category")

    def test_delete_category(self):
        """
        カテゴリ削除APIのテスト
        - ステータスコード204が返されること
        - カテゴリが正しく削除されること
        - 削除後、カテゴリの総数が1つ減ること
        """
        url = reverse("category-detail", args=[self.category.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 1)
