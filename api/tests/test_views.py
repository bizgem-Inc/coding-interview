from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Category, Company


class CategoryViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(name="株式会社テスト")
        cls.other_company = Company.objects.create(name="株式会社アザー")

    def setUp(self):
        self.parent = Category.objects.create(company=self.company, name="親カテゴリ")
        self.child = Category.objects.create(company=self.company, name="子カテゴリ", parent_category=self.parent)

    def list_url(self):
        return reverse("category-list")

    def detail_url(self, category_id):
        return reverse("category-detail", args=[category_id])

    def test_list(self):
        # 他企業のカテゴリも含め、全件が一覧で返ること
        other = Category.objects.create(company=self.other_company, name="他社カテゴリ")

        response = self.client.get(self.list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(
            {str(self.parent.id), str(self.child.id), str(other.id)},
            {item["id"] for item in response.data},
        )

        parent_data = next(item for item in response.data if item["id"] == str(self.parent.id))
        self.assertEqual(
            set(parent_data.keys()),
            {"id", "company", "name", "parent_category", "created_at", "updated_at"},
        )

    def test_retrieve(self):
        response = self.client.get(self.detail_url(self.child.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.child.id))
        self.assertEqual(response.data["company"], self.company.id)
        self.assertEqual(response.data["name"], "子カテゴリ")
        self.assertEqual(response.data["parent_category"], self.parent.id)

    def test_retrieve_not_found(self):
        response = self.client.get(self.detail_url("00000000-0000-0000-0000-000000000000"))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create(self):
        payload = {"company": str(self.company.id), "name": "新規カテゴリ", "parent_category": str(self.parent.id)}

        response = self.client.post(self.list_url(), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 3)

        created = Category.objects.get(id=response.data["id"])
        self.assertEqual(created.company_id, self.company.id)
        self.assertEqual(created.name, "新規カテゴリ")
        self.assertEqual(created.parent_category_id, self.parent.id)

    def test_create_without_parent_category(self):
        # parent_category は任意項目であること (ルートカテゴリの作成)
        payload = {"company": str(self.company.id), "name": "ルートカテゴリ"}

        response = self.client.post(self.list_url(), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data["parent_category"])
        self.assertIsNone(Category.objects.get(id=response.data["id"]).parent_category_id)

    def test_create_with_missing_required_fields(self):
        response = self.client.post(self.list_url(), {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("company", response.data)
        self.assertIn("name", response.data)
        self.assertEqual(Category.objects.count(), 2)

    def test_create_with_max_length_name(self):
        # name の上限 (255文字) ちょうどは作成できること
        payload = {"company": str(self.company.id), "name": "あ" * 255}

        response = self.client.post(self.list_url(), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(Category.objects.get(id=response.data["id"]).name), 255)

    def test_create_with_too_long_name(self):
        # 256文字は 400 になること (バイト数ではなく文字数で判定されること)
        payload = {"company": str(self.company.id), "name": "あ" * 256}

        response = self.client.post(self.list_url(), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(Category.objects.count(), 2)

    def test_create_with_blank_name(self):
        payload = {"company": str(self.company.id), "name": ""}

        response = self.client.post(self.list_url(), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(Category.objects.count(), 2)

    def test_update_with_too_long_name(self):
        response = self.client.patch(self.detail_url(self.child.id), {"name": "あ" * 256}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.child.refresh_from_db()
        self.assertEqual(self.child.name, "子カテゴリ")

    def test_create_with_duplicated_name_in_same_company(self):
        # (company, name) の一意制約違反は 500 ではなく 400 になること
        payload = {"company": str(self.company.id), "name": self.parent.name}

        response = self.client.post(self.list_url(), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Category.objects.count(), 2)

    def test_create_allows_same_name_in_other_company(self):
        # 一意制約は企業単位なので、他企業では同名カテゴリを作成できること
        payload = {"company": str(self.other_company.id), "name": self.parent.name}

        response = self.client.post(self.list_url(), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 3)

    def test_create_with_parent_category_of_other_company(self):
        payload = {
            "company": str(self.other_company.id),
            "name": "不正な親を持つカテゴリ",
            "parent_category": str(self.parent.id),
        }

        response = self.client.post(self.list_url(), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)
        self.assertEqual(Category.objects.count(), 2)

    def test_update(self):
        payload = {"company": str(self.company.id), "name": "更新後カテゴリ", "parent_category": None}

        response = self.client.put(self.detail_url(self.child.id), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.child.refresh_from_db()
        self.assertEqual(self.child.name, "更新後カテゴリ")
        self.assertIsNone(self.child.parent_category_id)

    def test_partial_update(self):
        response = self.client.patch(self.detail_url(self.child.id), {"name": "部分更新"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.child.refresh_from_db()
        self.assertEqual(self.child.name, "部分更新")
        # 指定していない項目は変更されないこと
        self.assertEqual(self.child.parent_category_id, self.parent.id)

    def test_partial_update_with_same_name_keeps_own_record(self):
        # 自分自身は一意制約チェックの対象外であること
        response = self.client.patch(self.detail_url(self.child.id), {"name": self.child.name}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_with_duplicated_name_in_same_company(self):
        response = self.client.patch(self.detail_url(self.child.id), {"name": self.parent.name}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.child.refresh_from_db()
        self.assertEqual(self.child.name, "子カテゴリ")

    def test_update_with_self_as_parent_category(self):
        response = self.client.patch(
            self.detail_url(self.child.id), {"parent_category": str(self.child.id)}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)
        self.child.refresh_from_db()
        self.assertEqual(self.child.parent_category_id, self.parent.id)

    def test_update_with_circular_parent_category(self):
        # parent -> child -> parent の循環を作れないこと
        response = self.client.patch(
            self.detail_url(self.parent.id), {"parent_category": str(self.child.id)}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)
        self.parent.refresh_from_db()
        self.assertIsNone(self.parent.parent_category_id)

    def test_update_not_found(self):
        response = self.client.patch(
            self.detail_url("00000000-0000-0000-0000-000000000000"), {"name": "更新"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_destroy(self):
        response = self.client.delete(self.detail_url(self.child.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.child.id).exists())

    def test_destroy_parent_sets_child_parent_category_to_null(self):
        # parent_category は on_delete=SET_NULL なので、子カテゴリは残ること
        response = self.client.delete(self.detail_url(self.parent.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.child.refresh_from_db()
        self.assertIsNone(self.child.parent_category_id)

    def test_destroy_not_found(self):
        response = self.client.delete(self.detail_url("00000000-0000-0000-0000-000000000000"))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
