from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company  # Companyモデルの場所に合わせてパスを調整するかも


class CategoryViewTests(APITestCase):
    def setUp(self):
        """
        各テストの前に毎回呼ばれる初期化処理。
        ここでテスト用の Company と Category を1件作っておく。
        """
        # ★ Company の必須フィールドに合わせて中身を調整してください
        # 例えば name 以外にも必須のカラムがあれば、ここに追加する必要があります。
        self.company = Company.objects.create(
            name="Test Company",
        )

        # 一覧・作成用のURL（/categories/）に対応
        self.list_url = reverse("category-list-create")

        # 1件取得・更新・削除用のテストデータ
        self.root_category = Category.objects.create(
            company=self.company,
            name="Root Category",
            parent_category=None,
        )

    def test_list(self):
        """
        GET /categories/ でカテゴリ一覧が取得できること
        """
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # setUpで1件作っているので、1件返ってくるはず
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Root Category")

    def test_retrieve(self):
        """
        GET /categories/<id>/ で1件取得できること
        """
        url = reverse("category-detail", kwargs={"pk": self.root_category.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.root_category.id))
        self.assertEqual(response.data["name"], "Root Category")

    def test_create(self):
        """
        POST /categories/ でカテゴリを作成できること
        """
        data = {
            "company": str(self.company.id),
            "name": "New Category",
            "parent_category": str(self.root_category.id),
        }
        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Root + New の2件になるはず
        self.assertEqual(Category.objects.count(), 2)

        created = Category.objects.get(name="New Category")
        self.assertEqual(created.company, self.company)
        self.assertEqual(created.parent_category, self.root_category)

    def test_update(self):
        """
        PUT /categories/<id>/ でカテゴリを更新できること
        """
        url = reverse("category-detail", kwargs={"pk": self.root_category.id})
        data = {
            "company": str(self.company.id),
            "name": "Updated Category",
            "parent_category": None,
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.root_category.refresh_from_db()
        self.assertEqual(self.root_category.name, "Updated Category")
        self.assertIsNone(self.root_category.parent_category)

    def test_destroy(self):
        """
        DELETE /categories/<id>/ でカテゴリを削除できること
        """
        url = reverse("category-detail", kwargs={"pk": self.root_category.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.root_category.id).exists())
