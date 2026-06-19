from django.urls import reverse
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        # 通常ケース用の企業と、企業境界のバリデーション確認用の企業を用意する。
        self.company = Company.objects.create(name="Acme Inc.")
        self.other_company = Company.objects.create(name="Other Inc.")
        self.category = Category.objects.create(company=self.company, name="Books")

    def test_list(self):
        # 一覧取得と、service層で指定した名前順の並びを確認する。
        Category.objects.create(company=self.company, name="Games")

        response = self.client.get(reverse("category-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["name"], "Books")

    def test_retrieve(self):
        # 詳細取得で、UUID・名前・企業IDが期待どおり返ることを確認する。
        response = self.client.get(reverse("category-detail", args=[self.category.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], str(self.category.id))
        self.assertEqual(response.data["name"], "Books")
        self.assertEqual(response.data["company"], self.company.id)

    def test_create(self):
        # 外部キーはUUID文字列で渡し、作成後にDBへ保存されることまで確認する。
        payload = {"company": str(self.company.id), "name": "Music"}

        response = self.client.post(reverse("category-list"), payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "Music")
        self.assertTrue(Category.objects.filter(company=self.company, name="Music").exists())

    def test_update(self):
        # PUTでカテゴリ名を更新し、DB上の値も変わっていることを確認する。
        payload = {"company": str(self.company.id), "name": "Novels", "parent_category": None}

        response = self.client.put(
            reverse("category-detail", args=[self.category.id]),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Novels")

    def test_destroy(self):
        # DELETE後に対象レコードがDBから消えていることを確認する。
        response = self.client.delete(reverse("category-detail", args=[self.category.id]))

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())

    def test_create_rejects_duplicate_name_in_same_company(self):
        # 同一企業内の同名カテゴリは、nameフィールドのエラーとして返す。
        payload = {"company": str(self.company.id), "name": "Books"}

        response = self.client.post(reverse("category-list"), payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("name", response.data)

    def test_create_allows_same_name_in_different_company(self):
        # 企業が異なる場合は、同じカテゴリ名でも作成を許可する。
        payload = {"company": str(self.other_company.id), "name": "Books"}

        response = self.client.post(reverse("category-list"), payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Category.objects.filter(name="Books").count(), 2)

    def test_create_rejects_parent_category_from_different_company(self):
        # 親カテゴリが別企業に属する場合は、親子関係を作らせない。
        parent_category = Category.objects.create(company=self.other_company, name="Parent")
        payload = {
            "company": str(self.company.id),
            "name": "Child",
            "parent_category": str(parent_category.id),
        }

        response = self.client.post(reverse("category-list"), payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("parent_category", response.data)

    def test_update_rejects_self_as_parent_category(self):
        # 自分自身を親カテゴリにする循環参照を拒否する。
        payload = {"parent_category": str(self.category.id)}

        response = self.client.patch(
            reverse("category-detail", args=[self.category.id]),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("parent_category", response.data)
