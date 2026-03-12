from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.response import Response

from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    """
    CategoryViewのテスト
    """

    company: Company
    category: Category
    list_url: str
    detail_url: str

    def setUp(self) -> None:
        self.company = Company.objects.create(name="テスト企業")
        self.category = Category.objects.create(name="テストカテゴリ", company=self.company)
        self.list_url = reverse("category-list")
        self.detail_url = reverse("category-detail", kwargs={"pk": self.category.id})

    def test_list(self) -> None:
        """一覧が取得できること"""
        response: Response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "テストカテゴリ")

    def test_retrieve(self) -> None:
        """詳細が取得できること"""
        response: Response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "テストカテゴリ")

    def test_create(self) -> None:
        """作成ができること"""
        data: dict = {"name": "新規カテゴリ", "company": self.company.id}
        response: Response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(name="新規カテゴリ").exists())

    def test_update(self) -> None:
        """更新ができること"""
        data: dict = {"name": "更新後カテゴリ", "company": self.company.id}
        response: Response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "更新後カテゴリ")

    def test_destroy(self) -> None:
        """削除ができること"""
        response: Response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())

    def test_create_duplicate_name_in_same_company(self) -> None:
        """同じ企業内での重複名のカテゴリ作成ができないこと"""
        data: dict = {"name": "テストカテゴリ", "company": self.company.id}
        response: Response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["non_field_errors"][0], "同じ企業内に同じ名前のカテゴリが既に存在します。")

    def test_create_with_parent_from_different_company(self) -> None:
        """別企業のカテゴリを親に設定できないこと"""
        other_company: Company = Company.objects.create(name="他企業")
        other_category: Category = Category.objects.create(name="他カテゴリ", company=other_company)
        data: dict = {"name": "不正な親カテゴリ", "company": self.company.id, "parent_category": other_category.id}
        response: Response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)

    def test_update_self_as_parent(self) -> None:
        """自分自身を親に設定できないこと"""
        data: dict = {"name": "テストカテゴリ", "company": self.company.id, "parent_category": self.category.id}
        response: Response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)

    def test_circular_dependency(self) -> None:
        """循環参照が発生する場合に設定できないこと"""
        cat_a: Category = Category.objects.create(name="カテゴリA", company=self.company)
        cat_b: Category = Category.objects.create(name="カテゴリB", company=self.company, parent_category=cat_a)

        # BをAの親に設定しようとする（A -> B -> A の循環）
        url: str = reverse("category-detail", kwargs={"pk": cat_a.id})
        data: dict = {"name": "カテゴリA", "company": self.company.id, "parent_category": cat_b.id}
        response: Response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["parent_category"][0], "循環参照が発生するため、このカテゴリを親に設定できません。")

    def test_max_depth_validation(self) -> None:
        """階層の深さ制限を超えて作成できないこと"""
        curr: Category = self.category
        for i in range(9):
            curr = Category.objects.create(name=f"カテゴリ{i}", company=self.company, parent_category=curr)

        # 11階層目を作ろうとする
        data: dict = {"name": "深すぎるカテゴリ", "company": self.company.id, "parent_category": curr.id}
        response: Response = self.client.post(self.list_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["parent_category"][0], "カテゴリの階層は最大10段階までです。")

    def test_patch_without_company_consistency_check(self) -> None:
        """PATCHリクエスト（companyなし）で不正な親が設定できないこと"""
        other_company: Company = Company.objects.create(name="他企業")
        other_category: Category = Category.objects.create(name="他カテゴリ", company=other_company)

        # companyを含まないPATCHリクエストで不正な親を設定しようとする
        data: dict = {"parent_category": other_category.id}
        response: Response = self.client.patch(self.detail_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["parent_category"][0], "親カテゴリは同じ企業に属している必要があります。")