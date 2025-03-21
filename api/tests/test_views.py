from rest_framework.test import APITestCase
from rest_framework import status
import uuid
from django.urls import reverse
from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="テスト会社")
        self.other_company = Company.objects.create(name="他社")

        self.parent_category = Category.objects.create(
            company=self.company, name="親カテゴリ"
        )
        self.category = Category.objects.create(
            company=self.company,
            name="テストカテゴリ",
            parent_category=self.parent_category,
        )

        self.other_company_category = Category.objects.create(
            company=self.other_company, name="他社カテゴリ"
        )

    def test_list(self):
        url = reverse("categories")
        response = self.client.get(url, {"company_id": self.company.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data), 2)

        category_ids = [category["id"] for category in response_data]
        self.assertIn(str(self.category.id), category_ids)
        self.assertIn(str(self.parent_category.id), category_ids)
        self.assertNotIn(str(self.other_company_category.id), category_ids)

    def test_retrieve(self):
        url = reverse("category-detail", kwargs={"category_id": self.category.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data["id"], str(self.category.id))
        self.assertEqual(response_data["name"], "テストカテゴリ")
        self.assertEqual(
            response_data["parent_category_id"], str(self.parent_category.id)
        )

    def test_create(self):
        data = {
            "name": "新規カテゴリ",
            "parent_category_id": str(self.parent_category.id),
            "company_id": str(self.company.id),
        }
        url = reverse("categories")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response_data = response.json()
        self.assertIsNotNone(response_data["id"])
        self.assertEqual(response_data["name"], "新規カテゴリ")
        category_id = uuid.UUID(response_data["id"])
        category = Category.objects.get(id=category_id)
        self.assertEqual(category.name, "新規カテゴリ")
        self.assertEqual(category.company.id, self.company.id)
        self.assertEqual(category.parent_category.id, self.parent_category.id)

    def test_create_without_parent_category(self):
        url = reverse("categories")
        data = {"name": "親なしカテゴリ", "company_id": str(self.company.id)}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.json()
        category_id = uuid.UUID(response_data["id"])
        category = Category.objects.get(id=category_id)
        self.assertEqual(category.name, "親なしカテゴリ")
        self.assertIsNone(category.parent_category)

    def test_create_invalid_data(self):
        url = reverse("categories")
        data = {"company_id": str(self.company.id)}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_missing_company_id(self):
        url = reverse("categories")
        data = {"name": "新規カテゴリ"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update(self):
        data = {"name": "更新カテゴリ"}
        url = reverse("category-detail", kwargs={"category_id": self.category.id})
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        category = Category.objects.get(id=self.category.id)
        self.assertEqual(category.name, "更新カテゴリ")
        self.assertIsNotNone(category.parent_category)
        self.assertEqual(category.parent_category.id, self.parent_category.id)

    def test_update_without_parent_category(self):
        url = reverse("category-detail", kwargs={"category_id": self.category.id})
        data = {"name": "更新カテゴリ", "parent_category_id": None}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        category = Category.objects.get(id=self.category.id)
        self.assertIsNone(category.parent_category)

    def test_update_invalid_data(self):
        url = reverse("category-detail", kwargs={"category_id": self.category.id})
        data = {"name": ""}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_invalid_parent_category_id(self):
        url = reverse("category-detail", kwargs={"category_id": self.category.id})
        data = {"parent_category_id": str(uuid.uuid4())}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_destroy(self):
        url = reverse("category-detail", kwargs={"category_id": self.category.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Category.DoesNotExist):
            Category.objects.get(id=self.category.id)
