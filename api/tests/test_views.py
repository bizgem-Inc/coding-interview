from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="企業A")
        self.other_company = Company.objects.create(name="企業B")
        self.category = Category.objects.create(company=self.company, name="家電")

    def list_url(self):
        return reverse("category-list")

    def detail_url(self, category):
        return reverse("category-detail", args=[category.pk])

    # --- CRUD ---

    def test_list(self):
        Category.objects.create(company=self.company, name="食品")

        response = self.client.get(self.list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([c["name"] for c in response.json()], ["家電", "食品"])

    def test_retrieve(self):
        child = Category.objects.create(company=self.company, name="テレビ", parent_category=self.category)

        response = self.client.get(self.detail_url(child))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        self.assertEqual(body["id"], str(child.pk))
        self.assertEqual(body["company"], str(self.company.pk))
        self.assertEqual(body["name"], "テレビ")
        self.assertEqual(body["parent_category"], str(self.category.pk))
        self.assertIn("created_at", body)
        self.assertIn("updated_at", body)

    def test_create(self):
        data = {"company": str(self.company.pk), "name": "食品"}

        response = self.client.post(self.list_url(), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Category.objects.get(pk=response.json()["id"])
        self.assertEqual(created.company, self.company)
        self.assertEqual(created.name, "食品")
        self.assertIsNone(created.parent_category)

    def test_create_with_parent(self):
        data = {"company": str(self.company.pk), "name": "テレビ", "parent_category": str(self.category.pk)}

        response = self.client.post(self.list_url(), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Category.objects.get(pk=response.json()["id"])
        self.assertEqual(created.parent_category, self.category)

    def test_update(self):
        parent = Category.objects.create(company=self.company, name="生活用品")
        data = {"company": str(self.company.pk), "name": "家電製品", "parent_category": str(parent.pk)}

        response = self.client.put(self.detail_url(self.category), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "家電製品")
        self.assertEqual(self.category.parent_category, parent)

    def test_partial_update(self):
        response = self.client.patch(self.detail_url(self.category), {"name": "家電製品"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "家電製品")

    def test_destroy(self):
        response = self.client.delete(self.detail_url(self.category))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(pk=self.category.pk).exists())

    def test_destroy_parent_keeps_children(self):
        # モデルの on_delete=SET_NULL により、子カテゴリは残り親が null になる
        child = Category.objects.create(company=self.company, name="テレビ", parent_category=self.category)

        response = self.client.delete(self.detail_url(self.category))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        child.refresh_from_db()
        self.assertIsNone(child.parent_category)

    # --- バリデーション ---

    def test_create_rejects_blank_name(self):
        for name in ["", "   "]:
            with self.subTest(name=name):
                data = {"company": str(self.company.pk), "name": name}

                response = self.client.post(self.list_url(), data, format="json")

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("name", response.json())
        self.assertEqual(Category.objects.count(), 1)

    def test_create_rejects_too_long_name(self):
        data = {"company": str(self.company.pk), "name": "a" * 256}

        response = self.client.post(self.list_url(), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.json())

    def test_create_rejects_duplicate_name_in_same_company(self):
        data = {"company": str(self.company.pk), "name": "家電"}

        response = self.client.post(self.list_url(), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["non_field_errors"], ["同じ企業内に同じ名前のカテゴリが既に存在します。"])
        self.assertEqual(Category.objects.count(), 1)

    def test_create_allows_same_name_in_other_company(self):
        data = {"company": str(self.other_company.pk), "name": "家電"}

        response = self.client.post(self.list_url(), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_rejects_duplicate_name_in_same_company(self):
        Category.objects.create(company=self.company, name="食品")

        response = self.client.patch(self.detail_url(self.category), {"name": "食品"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["non_field_errors"], ["同じ企業内に同じ名前のカテゴリが既に存在します。"])
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "家電")

    def test_create_rejects_parent_of_other_company(self):
        other_parent = Category.objects.create(company=self.other_company, name="家電")
        data = {"company": str(self.company.pk), "name": "テレビ", "parent_category": str(other_parent.pk)}

        response = self.client.post(self.list_url(), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["parent_category"], ["別の企業のカテゴリを親に指定することはできません。"])
        self.assertFalse(Category.objects.filter(name="テレビ").exists())

    def test_update_rejects_self_as_parent(self):
        response = self.client.patch(
            self.detail_url(self.category), {"parent_category": str(self.category.pk)}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["parent_category"], ["自分自身または子孫のカテゴリを親に指定することはできません。"])
        self.category.refresh_from_db()
        self.assertIsNone(self.category.parent_category)

    def test_update_rejects_descendant_as_parent(self):
        # 家電 <- テレビ <- 液晶テレビ の状態で、家電の親を液晶テレビにすると循環する
        child = Category.objects.create(company=self.company, name="テレビ", parent_category=self.category)
        grandchild = Category.objects.create(company=self.company, name="液晶テレビ", parent_category=child)

        response = self.client.patch(
            self.detail_url(self.category), {"parent_category": str(grandchild.pk)}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["parent_category"], ["自分自身または子孫のカテゴリを親に指定することはできません。"])
        self.category.refresh_from_db()
        self.assertIsNone(self.category.parent_category)

    def test_update_rejects_company_change(self):
        data = {"company": str(self.other_company.pk), "name": "家電"}

        response = self.client.put(self.detail_url(self.category), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["company"], ["作成後に企業を変更することはできません。"])
        self.category.refresh_from_db()
        self.assertEqual(self.category.company, self.company)
