from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(name="テスト企業")
        cls.parent = Category.objects.create(
            company=cls.company,
            name="親カテゴリ",
        )
        cls.category = Category.objects.create(
            company=cls.company,
            name="子カテゴリ",
            parent_category=cls.parent,
        )

    def test_list(self):
        response = self.client.get(reverse("category-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(
            {item["name"] for item in response.data},
            {"親カテゴリ", "子カテゴリ"},
        )

    def test_api_root_includes_category_endpoint(self):
        """APIルートにカテゴリ一覧のエンドポイントが表示されること。"""
        response = self.client.get(reverse("api-root"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("categories", response.data)

    def test_retrieve(self):
        response = self.client.get(
            reverse("category-detail", kwargs={"pk": self.category.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.category.pk))
        self.assertEqual(response.data["name"], "子カテゴリ")

    def test_create(self):
        payload = {
            "company": str(self.company.pk),
            "name": "新規カテゴリ",
            "parent_category": str(self.parent.pk),
        }

        response = self.client.post(
            reverse("category-list"),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Category.objects.filter(
                company=self.company,
                name="新規カテゴリ",
            ).exists()
        )

    def test_create_rejects_missing_required_fields(self):
        """Serializerにモデル由来の必須項目が反映されていること。"""
        response = self.client.post(
            reverse("category-list"),
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("company", response.data)
        self.assertIn("name", response.data)
        self.assertNotIn("parent_category", response.data)

    def test_create_rejects_duplicate_name_in_same_company(self):
        """同じ企業内では同名のカテゴリを作成できないこと。"""
        payload = {
            "company": str(self.company.pk),
            "name": self.parent.name,
        }

        response = self.client.post(
            reverse("category-list"),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            Category.objects.filter(
                company=self.company,
                name=self.parent.name,
            ).count(),
            1,
        )

    def test_create_allows_same_name_in_different_company(self):
        """異なる企業であれば同名のカテゴリを作成できること。"""
        another_company = Company.objects.create(name="別企業")
        payload = {
            "company": str(another_company.pk),
            "name": self.parent.name,
        }

        response = self.client.post(
            reverse("category-list"),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Category.objects.filter(
                company=another_company,
                name=self.parent.name,
            ).exists()
        )

    def test_create_rejects_parent_category_from_different_company(self):
        """異なる企業のカテゴリを親に指定して作成できないこと。"""
        another_company = Company.objects.create(name="別企業")
        another_parent = Category.objects.create(
            company=another_company,
            name="別企業の親カテゴリ",
        )
        payload = {
            "company": str(self.company.pk),
            "name": "不正な子カテゴリ",
            "parent_category": str(another_parent.pk),
        }

        response = self.client.post(
            reverse("category-list"),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(
            Category.objects.filter(
                company=self.company,
                name="不正な子カテゴリ",
            ).exists()
        )

    def test_create_allows_multiple_categories_with_same_parent(self):
        """同じ親カテゴリに複数の子カテゴリを紐づけられること。"""
        payload = {
            "company": str(self.company.pk),
            "name": "別の子カテゴリ",
            "parent_category": str(self.parent.pk),
        }

        response = self.client.post(
            reverse("category-list"),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Category.objects.filter(parent_category=self.parent).count(),
            2,
        )

    def test_update(self):
        payload = {
            "company": str(self.company.pk),
            "name": "更新後カテゴリ",
            "parent_category": str(self.parent.pk),
        }

        response = self.client.put(
            reverse("category-detail", kwargs={"pk": self.category.pk}),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "更新後カテゴリ")

    def test_update_rejects_duplicate_name_in_same_company(self):
        """同じ企業内の既存カテゴリと重複する名前へ更新できないこと。"""
        response = self.client.patch(
            reverse("category-detail", kwargs={"pk": self.category.pk}),
            {"name": self.parent.name},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "子カテゴリ")

    def test_update_allows_unchanged_name_in_same_company(self):
        """同じ企業内で自分自身と同じ名前のまま更新できること。"""
        response = self.client.patch(
            reverse("category-detail", kwargs={"pk": self.category.pk}),
            {"name": self.category.name},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Category.objects.filter(
                company=self.company,
                name=self.category.name,
            ).count(),
            1,
        )

    def test_update_rejects_self_as_parent_category(self):
        """自分自身を親カテゴリに指定して更新できないこと。"""
        response = self.client.patch(
            reverse("category-detail", kwargs={"pk": self.category.pk}),
            {"parent_category": str(self.category.pk)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.category.refresh_from_db()
        self.assertEqual(self.category.parent_category, self.parent)

    def test_update_rejects_company_change(self):
        """Categoryが属するCompanyを別のCompanyへ変更できないこと。"""
        another_company = Company.objects.create(name="別企業")

        response = self.client.patch(
            reverse("category-detail", kwargs={"pk": self.parent.pk}),
            {"company": str(another_company.pk)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data["company"][0]),
            "カテゴリが属する企業を変更することはできません。",
        )

        self.parent.refresh_from_db()
        self.assertEqual(self.parent.company, self.company)

    def test_destroy(self):
        response = self.client.delete(
            reverse("category-detail", kwargs={"pk": self.category.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Category.objects.filter(pk=self.category.pk).exists()
        )
