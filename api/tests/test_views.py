from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Category, Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        # テスト用のCompanyを作成
        self.company1 = Company.objects.create(name="Company 1")
        self.company2 = Company.objects.create(name="Company 2")

        # テスト用のCategoryを作成
        self.category1 = Category.objects.create(
            company=self.company1,
            name="Category 1"
        )
        self.category2 = Category.objects.create(
            company=self.company1,
            name="Category 2",
            parent_category=self.category1
        )

    def test_list(self):
        """カテゴリ一覧取得のテスト"""
        response = self.client.get("/api/categories/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve(self):
        """カテゴリ単体取得のテスト"""
        response = self.client.get(f"/api/categories/{self.category1.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Category 1")
        self.assertEqual(response.data["company"], self.company1.id)

    def test_create(self):
        """カテゴリ作成のテスト"""
        data = {
            "company": str(self.company1.id),
            "name": "New Category"
        }
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New Category")
        self.assertEqual(Category.objects.count(), 3)

    def test_create_with_parent_category(self):
        """親カテゴリ付きでカテゴリ作成のテスト"""
        data = {
            "company": str(self.company1.id),
            "name": "Child Category",
            "parent_category": str(self.category1.id)
        }
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["parent_category"], self.category1.id)

    def test_create_duplicate_name_same_company(self):
        """同一企業内で同名カテゴリを作成しようとした場合のバリデーションテスト"""
        data = {
            "company": str(self.company1.id),
            "name": "Category 1"  # 既に存在する名前
        }
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_duplicate_name_different_company(self):
        """異なる企業で同名カテゴリを作成できることのテスト"""
        data = {
            "company": str(self.company2.id),
            "name": "Category 1"  # company1では存在するが、company2では未存在
        }
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_without_required_fields(self):
        """必須フィールドなしでの作成時のバリデーションテスト"""
        # companyなし
        data = {"name": "Test"}
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # nameなし
        data = {"company": str(self.company1.id)}
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update(self):
        """カテゴリ更新のテスト"""
        data = {
            "company": str(self.company1.id),
            "name": "Updated Category"
        }
        response = self.client.put(
            f"/api/categories/{self.category1.id}/",
            data,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Category")

        # DBから再取得して確認
        self.category1.refresh_from_db()
        self.assertEqual(self.category1.name, "Updated Category")

    def test_partial_update(self):
        """カテゴリ部分更新のテスト"""
        data = {"name": "Partially Updated"}
        response = self.client.patch(
            f"/api/categories/{self.category1.id}/",
            data,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Partially Updated")

    def test_destroy(self):
        """カテゴリ削除のテスト"""
        category_id = self.category1.id
        response = self.client.delete(f"/api/categories/{category_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # 削除されたことを確認
        self.assertFalse(Category.objects.filter(id=category_id).exists())
        # 残りのカテゴリ数を確認
        self.assertEqual(Category.objects.count(), 1)

    def test_destroy_parent_category_sets_null(self):
        """親カテゴリ削除時、子カテゴリのparent_categoryがNullになることのテスト"""
        # category2はcategory1を親として持っている
        self.assertEqual(self.category2.parent_category, self.category1)

        # 親カテゴリを削除
        response = self.client.delete(f"/api/categories/{self.category1.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # 子カテゴリのparent_categoryがNullになっていることを確認
        self.category2.refresh_from_db()
        self.assertIsNone(self.category2.parent_category)
