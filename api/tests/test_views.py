import uuid

from rest_framework import status
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    """CategoryViewSet の CRUD テスト"""

    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(name="テスト企業")
        cls.other_company = Company.objects.create(name="別の企業")
        cls.parent_category = Category.objects.create(
            company=cls.company,
            name="親カテゴリ",
        )
        cls.child_category = Category.objects.create(
            company=cls.company,
            name="子カテゴリ",
            parent_category=cls.parent_category,
        )

    def setUp(self):
        self.list_url = "/api/categories/"
        self.parent_detail_url = f"/api/categories/{self.parent_category.id}/"
        self.child_detail_url = f"/api/categories/{self.child_category.id}/"

    # ------------------------------------------------------------------ #
    # 一覧取得 (LIST)
    # ------------------------------------------------------------------ #
    def test_list(self):
        """カテゴリ一覧を取得できること"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_empty(self):
        """カテゴリが存在しない場合、空リストが返ること"""
        Category.objects.all().delete()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    # ------------------------------------------------------------------ #
    # 詳細取得 (RETRIEVE)
    # ------------------------------------------------------------------ #
    def test_retrieve(self):
        """カテゴリ詳細を取得できること"""
        response = self.client.get(self.parent_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "親カテゴリ")
        self.assertEqual(str(response.data["id"]), str(self.parent_category.id))
        self.assertEqual(str(response.data["company"]), str(self.company.id))
        self.assertIsNone(response.data["parent_category"])
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)

    def test_retrieve_with_parent(self):
        """親カテゴリを持つカテゴリの詳細取得で parent_category が正しく返ること"""
        response = self.client.get(self.child_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data["parent_category"]), str(self.parent_category.id))

    def test_retrieve_not_found(self):
        """存在しないIDで404が返ること"""
        url = f"/api/categories/{uuid.uuid4()}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ------------------------------------------------------------------ #
    # 作成 (CREATE)
    # ------------------------------------------------------------------ #
    def test_create(self):
        """有効なデータでカテゴリを作成できること"""
        data = {
            "company": str(self.company.id),
            "name": "新カテゴリ",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "新カテゴリ")
        self.assertEqual(str(response.data["company"]), str(self.company.id))
        self.assertIsNone(response.data["parent_category"])
        self.assertTrue(Category.objects.filter(name="新カテゴリ").exists())

    def test_create_with_parent_category(self):
        """親カテゴリを指定してカテゴリを作成できること"""
        data = {
            "company": str(self.company.id),
            "name": "孫カテゴリ",
            "parent_category": str(self.parent_category.id),
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(str(response.data["parent_category"]), str(self.parent_category.id))

    def test_create_without_name(self):
        """name が未指定の場合 400 エラーが返ること"""
        data = {
            "company": str(self.company.id),
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_create_with_blank_name(self):
        """name が空文字の場合 400 エラーが返ること"""
        data = {
            "company": str(self.company.id),
            "name": "",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_with_whitespace_only_name(self):
        """name が空白文字のみの場合 400 エラーが返ること"""
        data = {
            "company": str(self.company.id),
            "name": "   ",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_without_company(self):
        """company が未指定の場合 400 エラーが返ること"""
        data = {
            "name": "テスト",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("company", response.data)

    def test_create_with_invalid_company(self):
        """存在しない company を指定した場合 400 エラーが返ること"""
        data = {
            "company": str(uuid.uuid4()),
            "name": "テスト",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("company", response.data)

    def test_create_duplicate_name_in_same_company(self):
        """同じ企業内で重複するカテゴリ名の場合 400 エラーが返ること"""
        data = {
            "company": str(self.company.id),
            "name": "親カテゴリ",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_create_same_name_in_different_company(self):
        """異なる企業であれば同じカテゴリ名で作成できること"""
        data = {
            "company": str(self.other_company.id),
            "name": "親カテゴリ",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_parent_category_different_company(self):
        """親カテゴリが異なる企業のものの場合 400 エラーが返ること"""
        other_category = Category.objects.create(
            company=self.other_company,
            name="他社カテゴリ",
        )
        data = {
            "company": str(self.company.id),
            "name": "新カテゴリ2",
            "parent_category": str(other_category.id),
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)

    def test_create_with_invalid_parent_category(self):
        """存在しない parent_category を指定した場合 400 エラーが返ること"""
        data = {
            "company": str(self.company.id),
            "name": "テスト",
            "parent_category": str(uuid.uuid4()),
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)

    # ------------------------------------------------------------------ #
    # 更新 (UPDATE / PARTIAL UPDATE)
    # ------------------------------------------------------------------ #
    def test_update(self):
        """PUT でカテゴリを更新できること"""
        data = {
            "company": str(self.company.id),
            "name": "更新カテゴリ名",
        }
        response = self.client.put(self.parent_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "更新カテゴリ名")
        self.parent_category.refresh_from_db()
        self.assertEqual(self.parent_category.name, "更新カテゴリ名")

    def test_partial_update(self):
        """PATCH でカテゴリを部分更新できること"""
        data = {"name": "部分更新カテゴリ名"}
        response = self.client.patch(self.parent_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "部分更新カテゴリ名")
        self.parent_category.refresh_from_db()
        self.assertEqual(self.parent_category.name, "部分更新カテゴリ名")

    def test_update_with_duplicate_name(self):
        """同じ企業内で重複する名前に更新しようとすると 400 エラーが返ること"""
        data = {
            "company": str(self.company.id),
            "name": "子カテゴリ",
        }
        response = self.client.put(self.parent_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_circular_reference(self):
        """循環参照が発生する親カテゴリ設定で 400 エラーが返ること"""
        # 親カテゴリの parent_category に子カテゴリを設定 → 循環参照
        data = {
            "company": str(self.company.id),
            "name": "親カテゴリ",
            "parent_category": str(self.child_category.id),
        }
        response = self.client.put(self.parent_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)

    def test_update_self_reference(self):
        """自分自身を親カテゴリに設定すると 400 エラーが返ること"""
        data = {
            "company": str(self.company.id),
            "name": "親カテゴリ",
            "parent_category": str(self.parent_category.id),
        }
        response = self.client.put(self.parent_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)

    def test_update_not_found(self):
        """存在しないIDで更新すると 404 が返ること"""
        url = f"/api/categories/{uuid.uuid4()}/"
        data = {
            "company": str(self.company.id),
            "name": "テスト",
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ------------------------------------------------------------------ #
    # 削除 (DESTROY)
    # ------------------------------------------------------------------ #
    def test_destroy(self):
        """カテゴリを削除できること"""
        category = Category.objects.create(
            company=self.company,
            name="削除用カテゴリ",
        )
        url = f"/api/categories/{category.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=category.id).exists())

    def test_destroy_not_found(self):
        """存在しないIDで削除すると 404 が返ること"""
        url = f"/api/categories/{uuid.uuid4()}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_destroy_parent_sets_null(self):
        """親カテゴリを削除すると子カテゴリの parent_category が NULL になること"""
        parent = Category.objects.create(company=self.company, name="削除親")
        child = Category.objects.create(
            company=self.company, name="削除子", parent_category=parent
        )
        url = f"/api/categories/{parent.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        child.refresh_from_db()
        self.assertIsNone(child.parent_category)

    # ------------------------------------------------------------------ #
    # バリデーション追加テスト
    # ------------------------------------------------------------------ #
    def test_name_max_length(self):
        """name が 255 文字を超える場合 400 エラーが返ること"""
        data = {
            "company": str(self.company.id),
            "name": "あ" * 256,
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_name_exactly_max_length(self):
        """name が 255 文字の場合は正常に作成できること"""
        data = {
            "company": str(self.company.id),
            "name": "a" * 255,
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_name_is_trimmed(self):
        """name の前後の空白がトリムされること"""
        data = {
            "company": str(self.company.id),
            "name": "  トリムテスト  ",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "トリムテスト")

    def test_read_only_fields_ignored_on_create(self):
        """id, created_at, updated_at はリクエストで指定しても無視されること"""
        custom_id = str(uuid.uuid4())
        data = {
            "id": custom_id,
            "company": str(self.company.id),
            "name": "読み取り専用テスト",
            "created_at": "2000-01-01T00:00:00Z",
            "updated_at": "2000-01-01T00:00:00Z",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # 指定したIDは無視され、自動生成されたIDが使用される
        self.assertNotEqual(response.data["id"], custom_id)
