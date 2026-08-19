import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="テスト企業")
        self.other_company = Company.objects.create(name="別のテスト企業")
        self.parent_category = Category.objects.create(company=self.company, name="親カテゴリ")
        self.category = Category.objects.create(company=self.company, name="子カテゴリ", parent_category=self.parent_category)
        self.other_company_category = Category.objects.create(company=self.other_company, name="別企業のカテゴリ")

    def test_list(self):
        response = self.client.get(reverse("category-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        self.assertEqual(len(body), 3)
        self.assertEqual(
            {row["id"] for row in body},
            {str(self.parent_category.id), str(self.category.id), str(self.other_company_category.id)},
        )

    def test_retrieve(self):
        response = self.client.get(reverse("category-detail", args=[self.category.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        self.assertEqual(set(body), {"id", "company", "name", "parent_category", "created_at", "updated_at"})
        self.assertEqual(body["id"], str(self.category.id))
        self.assertEqual(body["company"], str(self.company.id))
        self.assertEqual(body["name"], "子カテゴリ")
        self.assertEqual(body["parent_category"], str(self.parent_category.id))
        self.assertIsNotNone(body["created_at"])
        self.assertIsNotNone(body["updated_at"])

    def test_retrieve_returns_404_for_unknown_id(self):
        response = self.client.get(reverse("category-detail", args=[uuid.uuid4()]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create(self):
        payload = {"company": str(self.company.id), "name": "新規カテゴリ", "parent_category": str(self.parent_category.id)}

        response = self.client.post(reverse("category-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Category.objects.get(id=response.json()["id"])
        self.assertEqual(created.name, "新規カテゴリ")
        self.assertEqual(created.company_id, self.company.id)
        self.assertEqual(created.parent_category_id, self.parent_category.id)

    def test_create_without_parent_category(self):
        payload = {"company": str(self.company.id), "name": "親を持たないカテゴリ"}

        response = self.client.post(reverse("category-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(Category.objects.get(id=response.json()["id"]).parent_category)

    def test_create_ignores_read_only_fields(self):
        specified_id = uuid.uuid4()
        payload = {
            "id": str(specified_id),
            "company": str(self.company.id),
            "name": "読み取り専用フィールド検証カテゴリ",
            "created_at": "2000-01-01T00:00:00Z",
            "updated_at": "2000-01-01T00:00:00Z",
        }

        response = self.client.post(reverse("category-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Category.objects.get(id=response.json()["id"])
        self.assertNotEqual(created.id, specified_id)
        self.assertNotEqual(created.created_at.year, 2000)
        self.assertNotEqual(created.updated_at.year, 2000)

    def test_update(self):
        payload = {"company": str(self.company.id), "name": "更新後カテゴリ", "parent_category": None}

        response = self.client.put(reverse("category-detail", args=[self.category.id]), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "更新後カテゴリ")
        self.assertIsNone(self.category.parent_category)

    def test_partial_update(self):
        payload = {"name": "部分更新後カテゴリ"}

        response = self.client.patch(reverse("category-detail", args=[self.category.id]), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "部分更新後カテゴリ")
        self.assertEqual(self.category.parent_category_id, self.parent_category.id)

    def test_destroy(self):
        response = self.client.delete(reverse("category-detail", args=[self.category.id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())

    def test_destroy_returns_404_for_unknown_id(self):
        response = self.client.delete(reverse("category-detail", args=[uuid.uuid4()]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_destroy_parent_category_keeps_child_with_null_parent_category(self):
        response = self.client.delete(reverse("category-detail", args=[self.parent_category.id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.category.refresh_from_db()
        self.assertIsNone(self.category.parent_category)

    def test_create_requires_company(self):
        response = self.client.post(reverse("category-list"), {"name": "企業なしカテゴリ"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("company", response.json())

    def test_create_rejects_unknown_company(self):
        payload = {"company": str(uuid.uuid4()), "name": "存在しない企業のカテゴリ"}

        response = self.client.post(reverse("category-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("company", response.json())

    def test_create_requires_name(self):
        response = self.client.post(reverse("category-list"), {"company": str(self.company.id)}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.json())

    def test_create_rejects_blank_name(self):
        payload = {"company": str(self.company.id), "name": "   "}

        response = self.client.post(reverse("category-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.json())

    def test_create_rejects_name_longer_than_max_length(self):
        payload = {"company": str(self.company.id), "name": "a" * 256}

        response = self.client.post(reverse("category-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.json())

    def test_create_rejects_duplicate_name_in_same_company(self):
        payload = {"company": str(self.company.id), "name": self.category.name}

        response = self.client.post(reverse("category-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.json())

    def test_create_allows_duplicate_name_in_another_company(self):
        payload = {"company": str(self.other_company.id), "name": self.category.name}

        response = self.client.post(reverse("category-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Category.objects.get(id=response.json()["id"])
        self.assertEqual(created.name, self.category.name)
        self.assertEqual(created.company_id, self.other_company.id)

    def test_update_rejects_duplicate_name_in_same_company(self):
        payload = {"company": str(self.company.id), "name": self.parent_category.name}

        response = self.client.put(reverse("category-detail", args=[self.category.id]), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.json())

    def test_update_allows_keeping_its_own_name(self):
        payload = {"company": str(self.company.id), "name": self.category.name}

        response = self.client.put(reverse("category-detail", args=[self.category.id]), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_rejects_itself_as_parent_category(self):
        payload = {"company": str(self.company.id), "name": self.category.name, "parent_category": str(self.category.id)}

        response = self.client.put(reverse("category-detail", args=[self.category.id]), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.json())

    def test_partial_update_rejects_itself_as_parent_category(self):
        payload = {"parent_category": str(self.category.id)}

        response = self.client.patch(reverse("category-detail", args=[self.category.id]), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.json())

    def test_create_rejects_parent_category_in_another_company(self):
        payload = {
            "company": str(self.company.id),
            "name": "別企業を親に持つカテゴリ",
            "parent_category": str(self.other_company_category.id),
        }

        response = self.client.post(reverse("category-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.json())

    def test_partial_update_rejects_parent_category_in_another_company(self):
        payload = {"parent_category": str(self.other_company_category.id)}

        response = self.client.patch(reverse("category-detail", args=[self.category.id]), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.json())

    def test_partial_update_rejects_company_change_conflicting_with_parent_category(self):
        payload = {"company": str(self.other_company.id)}

        response = self.client.patch(reverse("category-detail", args=[self.category.id]), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.json())
