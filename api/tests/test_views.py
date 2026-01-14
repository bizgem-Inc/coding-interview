from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.company import Company
from api.models.category import Category


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Company")

    def test_list(self):
        Category.objects.create(company=self.company, name="Test Category A")
        Category.objects.create(company=self.company, name="Test Category B")
        
        url = reverse("category-list")
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_retrieve(self):
        category = Category.objects.create(company=self.company, name="Test Category A")

        url = reverse("category-detail", kwargs={"pk": str(category.id)})
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["id"], str(category.id))
        self.assertEqual(res.data["company"], self.company.id)
        self.assertEqual(res.data["name"], "Test Category A")
        self.assertIsNone(res.data["parent_category"])

    def test_create(self):
        url = reverse("category-list")
        payload = {
            "company": str(self.company.id),
            "name": "New Category",
            "parent_category": None,
        }

        res = self.client.post(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(Category.objects.first().name, "New Category")

        # 重複チェック
        res = self.client.post(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", res.data)
        # エラー文言のチェックまで厳密に行う必要がなければ以下の検証は不要
        self.assertEqual(res.data["name"][0], "同じ企業に同名のカテゴリが既に存在します。")

    def test_update(self):
        category = Category.objects.create(company=self.company, name="Before")

        url = reverse("category-detail", kwargs={"pk": str(category.id)})
        payload = {"name": "After"}

        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        category.refresh_from_db()
        self.assertEqual(category.name, "After")

    def test_destroy(self):
        category = Category.objects.create(company=self.company, name="ToDelete")

        url = reverse("category-detail", kwargs={"pk": str(category.id)})
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(pk=category.id).exists())
