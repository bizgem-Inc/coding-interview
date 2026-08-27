import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Category, Company


class CategoryViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(name="テスト企業")
        cls.other_company = Company.objects.create(name="別企業")
        cls.parent = Category.objects.create(company=cls.company, name="親カテゴリ")
        cls.child = Category.objects.create(
            company=cls.company, name="子カテゴリ", parent_category=cls.parent
        )

    def list_url(self):
        return reverse("category-list")

    def detail_url(self, category):
        return reverse("category-detail", args=[category.pk])

    def test_list(self):
        response = self.client.get(self.list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [row["id"] for row in response.data],
            [str(self.parent.pk), str(self.child.pk)],
        )

    def test_retrieve(self):
        response = self.client.get(self.detail_url(self.child))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "子カテゴリ")
        self.assertEqual(response.data["company"], self.company.pk)
        self.assertEqual(response.data["parent_category"], self.parent.pk)

    def test_retrieve_returns_404_for_unknown_id(self):
        response = self.client.get(reverse("category-detail", args=[uuid.uuid4()]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create(self):
        payload = {
            "company": str(self.company.pk),
            "name": "新規カテゴリ",
            "parent_category": str(self.parent.pk),
        }

        response = self.client.post(self.list_url(), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Category.objects.get(pk=response.data["id"])
        self.assertEqual(created.name, "新規カテゴリ")
        self.assertEqual(created.company, self.company)
        self.assertEqual(created.parent_category, self.parent)

    def test_create_without_parent_category(self):
        payload = {"company": str(self.company.pk), "name": "ルートカテゴリ"}

        response = self.client.post(self.list_url(), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(Category.objects.get(pk=response.data["id"]).parent_category)

    def test_create_requires_company_and_name(self):
        response = self.client.post(self.list_url(), {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("company", response.data)
        self.assertIn("name", response.data)

    def test_create_rejects_duplicate_name_in_same_company(self):
        payload = {"company": str(self.company.pk), "name": self.parent.name}

        response = self.client.post(self.list_url(), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_create_allows_duplicate_name_in_other_company(self):
        payload = {"company": str(self.other_company.pk), "name": self.parent.name}

        response = self.client.post(self.list_url(), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_rejects_parent_category_of_other_company(self):
        payload = {
            "company": str(self.other_company.pk),
            "name": "別企業のカテゴリ",
            "parent_category": str(self.parent.pk),
        }

        response = self.client.post(self.list_url(), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)

    def test_update(self):
        response = self.client.patch(
            self.detail_url(self.child), {"name": "更新後カテゴリ"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.child.refresh_from_db()
        self.assertEqual(self.child.name, "更新後カテゴリ")

    def test_update_with_put_keeping_own_name(self):
        payload = {
            "company": str(self.company.pk),
            "name": self.child.name,
            "parent_category": None,
        }

        response = self.client.put(self.detail_url(self.child), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.child.refresh_from_db()
        self.assertIsNone(self.child.parent_category)

    def test_update_rejects_itself_as_parent_category(self):
        response = self.client.patch(
            self.detail_url(self.parent),
            {"parent_category": str(self.parent.pk)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)

    def test_update_rejects_descendant_as_parent_category(self):
        response = self.client.patch(
            self.detail_url(self.parent),
            {"parent_category": str(self.child.pk)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)

    def test_destroy(self):
        response = self.client.delete(self.detail_url(self.child))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(pk=self.child.pk).exists())
