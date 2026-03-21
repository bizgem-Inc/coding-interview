from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Category, Company


class CategoryViewTests(APITestCase):
    """Category CRUD API のテスト"""

    def setUp(self):
        """各テストで共通して使うデータを準備"""
        self.company = Company.objects.create(name="テスト企業")

    def test_list(self):
        """一覧取得: GET /api/categories/ でカテゴリ一覧が返ること"""
        Category.objects.create(company=self.company, name="カテゴリA")
        Category.objects.create(company=self.company, name="カテゴリB")

        url = reverse("category-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve(self):
        """1件取得: GET /api/categories/{id}/ でカテゴリ1件が返ること"""
        category = Category.objects.create(company=self.company, name="カテゴリA")

        url = reverse("category-detail", kwargs={"pk": category.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "カテゴリA")
        self.assertEqual(str(response.data["company"]), str(self.company.id))

    def test_create(self):
        """作成: POST /api/categories/ でカテゴリが作成されること"""
        url = reverse("category-list")
        data = {"company": str(self.company.id), "name": "新規カテゴリ"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "新規カテゴリ")
        self.assertTrue(Category.objects.filter(name="新規カテゴリ").exists())

    def test_create_with_parent_category(self):
        """作成: parent_category を指定して作成できること"""
        parent = Category.objects.create(company=self.company, name="親カテゴリ")
        url = reverse("category-list")
        data = {
            "company": str(self.company.id),
            "name": "子カテゴリ",
            "parent_category": str(parent.id),
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(str(response.data["parent_category"]), str(parent.id))

    def test_create_without_required_fields_fails(self):
        """作成: company や name なしでは作成できないこと（バリデーション）"""
        url = reverse("category-list")

        response = self.client.post(url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_duplicate_name_in_same_company_fails(self):
        """作成: 同一企業内で同名カテゴリは作成できないこと（バリデーション）"""
        Category.objects.create(company=self.company, name="重複カテゴリ")
        url = reverse("category-list")
        data = {"company": str(self.company.id), "name": "重複カテゴリ"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update(self):
        """更新: PUT /api/categories/{id}/ でカテゴリが更新されること"""
        category = Category.objects.create(company=self.company, name="更新前")
        url = reverse("category-detail", kwargs={"pk": category.id})
        data = {"company": str(self.company.id), "name": "更新後"}

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        category.refresh_from_db()
        self.assertEqual(category.name, "更新後")

    def test_destroy(self):
        """削除: DELETE /api/categories/{id}/ でカテゴリが削除されること"""
        category = Category.objects.create(company=self.company, name="削除対象")
        url = reverse("category-detail", kwargs={"pk": category.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=category.id).exists())
