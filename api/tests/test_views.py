from rest_framework.test import APITestCase
from django.urls import reverse

from api.models.company import Company
from api.models.category import Category

class CategoryViewTests(APITestCase):
    def test_list(self):
        """
        GET /api/categories/

        一覧取得ができること（HTTP 200）と、最低限の件数が期待通りであることを確認する。
        """
        company = Company.objects.create(name="C1")
        Category.objects.create(company=company, name="cat-1")

        url = reverse("category-list")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        # listの戻りは順序や返却フィールド変更で壊れやすいので、ここでは件数のみ検証する
        self.assertEqual(len(res.json()), 1)

    def test_retrieve(self):
        """
        GET /api/categories/{id}/

        1件取得ができること（HTTP 200）と、取得したレコードが期待したID/名前であることを確認する。
        """
        company = Company.objects.create(name="C1")
        category = Category.objects.create(company=company, name="cat-1")

        url = reverse("category-detail", kwargs={"pk": str(category.id)})
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["id"], str(category.id))
        self.assertEqual(res.json()["name"], "cat-1")

    def test_create(self):
        """
        POST /api/categories/

        作成ができること（HTTP 201）と、レスポンスおよびDBに保存された値が期待通りであることを確認する。
        """
        company = Company.objects.create(name="C1")

        url = reverse("category-list")
        res = self.client.post(
            url,
            data={"company": str(company.id), "name": "cat-1", "parent_category": None},
            format="json",
        )

        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()["name"], "cat-1")
        self.assertTrue(Category.objects.filter(company=company, name="cat-1").exists())

    def test_create_duplicate_name_in_same_company_returns_400(self):
        """
        POST /api/categories/

        同一企業内で同名カテゴリを作成しようとした場合に、バリデーションエラー（HTTP 400）になることを確認する。
        """
        company = Company.objects.create(name="C1")
        Category.objects.create(company=company, name="cat-1")

        url = reverse("category-list")
        res = self.client.post(url, data={"company": str(company.id), "name": "cat-1"}, format="json")

        self.assertEqual(res.status_code, 400)
        self.assertIn("name", res.json())

    def test_update_duplicate_name_in_same_company_returns_400(self):
        """
        PATCH /api/categories/{id}/

        更新で同一企業内の既存カテゴリ名に変更しようとした場合に、バリデーションエラー（HTTP 400）になることを確認する。
        """
        company = Company.objects.create(name="C1")
        Category.objects.create(company=company, name="cat-1")
        category = Category.objects.create(company=company, name="cat-2")

        url = reverse("category-detail", kwargs={"pk": str(category.id)})
        res = self.client.patch(url, data={"name": "cat-1"}, format="json")

        self.assertEqual(res.status_code, 400)
        self.assertIn("name", res.json())

    def test_update(self):
        """
        PATCH /api/categories/{id}/

        一部更新（PATCH）ができること（HTTP 200）と、DBの値が更新されていることを確認する。
        """
        company = Company.objects.create(name="C1")
        category = Category.objects.create(company=company, name="cat-1")

        url = reverse("category-detail", kwargs={"pk": str(category.id)})
        res = self.client.patch(url, data={"name": "cat-2"}, format="json")

        self.assertEqual(res.status_code, 200)
        category.refresh_from_db()
        self.assertEqual(category.name, "cat-2")

    def test_update_self_parent_category_returns_400(self):
        """
        PATCH /api/categories/{id}/

        親カテゴリに自分自身を指定した場合に、バリデーションエラー（HTTP 400）になることを確認する。
        """
        company = Company.objects.create(name="C1")
        category = Category.objects.create(company=company, name="cat-1")

        url = reverse("category-detail", kwargs={"pk": str(category.id)})
        res = self.client.patch(url, data={"parent_category": str(category.id)}, format="json")

        self.assertEqual(res.status_code, 400)
        self.assertIn("parent_category", res.json())

    def test_create_parent_from_other_company_returns_400(self):
        """
        POST /api/categories/

        別企業のカテゴリを親に指定した場合に、バリデーションエラー（HTTP 400）になることを確認する。
        """
        company1 = Company.objects.create(name="C1")
        company2 = Company.objects.create(name="C2")
        parent = Category.objects.create(company=company1, name="parent")

        url = reverse("category-list")
        res = self.client.post(
            url,
            data={"company": str(company2.id), "name": "child", "parent_category": str(parent.id)},
            format="json",
        )

        self.assertEqual(res.status_code, 400)
        self.assertIn("parent_category", res.json())

    def test_update_parent_from_other_company_returns_400(self):
        """
        PATCH /api/categories/{id}/

        別企業のカテゴリを親に指定した場合に、バリデーションエラー（HTTP 400）になることを確認する。
        """
        company1 = Company.objects.create(name="C1")
        company2 = Company.objects.create(name="C2")
        parent = Category.objects.create(company=company1, name="parent")
        category = Category.objects.create(company=company2, name="child")

        url = reverse("category-detail", kwargs={"pk": str(category.id)})
        res = self.client.patch(url, data={"parent_category": str(parent.id)}, format="json")

        self.assertEqual(res.status_code, 400)
        self.assertIn("parent_category", res.json())

    def test_update_descendant_as_parent_returns_400(self):
        """
        PATCH /api/categories/{id}/

        子孫カテゴリを親に指定した場合（循環参照）に、バリデーションエラー（HTTP 400）になることを確認する。
        """
        company = Company.objects.create(name="C1")
        parent = Category.objects.create(company=company, name="parent")
        child = Category.objects.create(company=company, name="child", parent_category=parent)
        grandchild = Category.objects.create(company=company, name="grandchild", parent_category=child)

        url = reverse("category-detail", kwargs={"pk": str(parent.id)})
        res = self.client.patch(url, data={"parent_category": str(grandchild.id)}, format="json")

        self.assertEqual(res.status_code, 400)
        self.assertIn("parent_category", res.json())

    def test_destroy(self):
        """
        DELETE /api/categories/{id}/

        削除ができること（HTTP 204）と、DBから対象レコードが削除されていることを確認する。
        """
        company = Company.objects.create(name="C1")
        category = Category.objects.create(company=company, name="cat-1")

        url = reverse("category-detail", kwargs={"pk": str(category.id)})
        res = self.client.delete(url)

        self.assertEqual(res.status_code, 204)
        self.assertFalse(Category.objects.filter(id=category.id).exists())
