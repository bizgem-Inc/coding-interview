import uuid

from rest_framework import status
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    """CategoryViewSet の CRUD テスト"""

    def setUp(self):
        """テスト用の Company と Category を作成"""
        self.company = Company.objects.create(name="テスト企業")
        self.category = Category.objects.create(
            company=self.company,
            name="テストカテゴリ",
        )
        self.list_url = "/api/categories/"
        self.detail_url = f"/api/categories/{self.category.id}/"

    # ===== 正常系 =====

    def test_list(self):
        """カテゴリ一覧を取得できること"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve(self):
        """カテゴリ詳細を取得できること"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "テストカテゴリ")

    def test_create(self):
        """カテゴリを作成できること"""
        data = {
            "company": str(self.company.id),
            "name": "新規カテゴリ",
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "新規カテゴリ")
        self.assertEqual(Category.objects.count(), 2)

    def test_update(self):
        """カテゴリを更新できること"""
        data = {
            "company": str(self.company.id),
            "name": "更新後カテゴリ",
        }
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "更新後カテゴリ")

    def test_destroy(self):
        """カテゴリを削除できること"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 0)

    def test_partial_update(self):
        """PATCH で名前だけ部分更新できること"""
        data = {"name": "部分更新カテゴリ"}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "部分更新カテゴリ")

    def test_create_with_parent_category(self):
        """parent_category を指定してカテゴリを作成できること"""
        data = {
            "company": str(self.company.id),
            "name": "子カテゴリ",
            "parent_category": str(self.category.id),
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(str(response.data["parent_category"]), str(self.category.id))

    def test_create_with_null_parent_category(self):
        """parent_category を null で作成できること"""
        data = {
            "company": str(self.company.id),
            "name": "ルートカテゴリ",
            "parent_category": None,
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data["parent_category"])

    # ===== 異常系 =====

    def test_create_without_required_fields(self):
        """必須フィールドなしで作成すると400エラーになること"""
        response = self.client.post(self.list_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("company", response.data)
        self.assertIn("name", response.data)

    def test_create_with_duplicate_company_name(self):
        """同一企業で同名カテゴリを作成すると400エラーになること（UniqueConstraint）"""
        data = {
            "company": str(self.company.id),
            "name": "テストカテゴリ",  # setUpで既に作成済み
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_with_nonexistent_company(self):
        """存在しない企業IDで作成すると400エラーになること"""
        data = {
            "company": str(uuid.uuid4()),
            "name": "新規カテゴリ",
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_with_nonexistent_parent_category(self):
        """存在しないparent_category IDで作成すると400エラーになること"""
        data = {
            "company": str(self.company.id),
            "name": "子カテゴリ",
            "parent_category": str(uuid.uuid4()),
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_with_empty_name(self):
        """空文字の名前で作成すると400エラーになること"""
        data = {
            "company": str(self.company.id),
            "name": "",
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_nonexistent(self):
        """存在しないカテゴリIDで詳細取得すると404エラーになること"""
        url = f"/api/categories/{uuid.uuid4()}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_nonexistent(self):
        """存在しないカテゴリIDで更新すると404エラーになること"""
        url = f"/api/categories/{uuid.uuid4()}/"
        data = {
            "company": str(self.company.id),
            "name": "更新",
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_destroy_nonexistent(self):
        """存在しないカテゴリIDで削除すると404エラーになること"""
        url = f"/api/categories/{uuid.uuid4()}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
