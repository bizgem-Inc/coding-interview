from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Company")
        self.category = Category.objects.create(
            company=self.company,
            name="Test Category"
        )

    def test_list(self):
        response = self.client.get("/api/categories/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Test Category")

    def test_retrieve(self):
        response = self.client.get(f"/api/categories/{self.category.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Category")

    def test_create(self):
        data = {
            "company": self.company.id,
            "name": "New Category"
        }
        response = self.client.post("/api/categories/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New Category")
        self.assertTrue(Category.objects.filter(name="New Category").exists())

    def test_update(self):
        data = {
            "company": self.company.id,
            "name": "Updated Category"
        }
        response = self.client.put(f"/api/categories/{self.category.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Category")
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Updated Category")

    def test_create_with_parent_category(self):
        parent_category = Category.objects.create(
            company=self.company,
            name="Parent Category"
        )
        data = {
            "company": self.company.id,
            "name": "Child Category",
            "parent_category": parent_category.id
        }
        response = self.client.post("/api/categories/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Child Category")
        self.assertEqual(str(response.data["parent_category"]), str(parent_category.id))

        child_category = Category.objects.get(name="Child Category")
        self.assertEqual(child_category.parent_category, parent_category)

    def test_create_with_invalid_parent_category(self):
        import uuid

        fake_uuid = str(uuid.uuid4())
        data = {
            "company": self.company.id,
            "name": "Child Category",
            "parent_category": fake_uuid
        }
        response = self.client.post("/api/categories/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_with_parent_category(self):
        parent_category = Category.objects.create(
            company=self.company,
            name="Parent Category"
        )
        data = {
            "company": self.company.id,
            "name": "Updated Category with Parent",
            "parent_category": parent_category.id
        }
        response = self.client.put(f"/api/categories/{self.category.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Category with Parent")
        self.assertEqual(str(response.data["parent_category"]), str(parent_category.id))

        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Updated Category with Parent")
        self.assertEqual(self.category.parent_category, parent_category)

    def test_update_remove_parent_category(self):
        parent_category = Category.objects.create(
            company=self.company,
            name="Parent Category"
        )
        self.category.parent_category = parent_category
        self.category.save()

        data = {
            "parent_category": ""
        }
        response = self.client.patch(f"/api/categories/{self.category.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Category")
        self.assertIsNone(response.data["parent_category"])

        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Test Category")
        self.assertIsNone(self.category.parent_category)

    def test_update_with_invalid_parent_category(self):
        import uuid

        fake_uuid = str(uuid.uuid4())
        data = {
            "company": self.company.id,
            "name": "Updated Category",
            "parent_category": fake_uuid
        }
        response = self.client.put(f"/api/categories/{self.category.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_self_reference_error(self):
        data = {
            "company": self.company.id,
            "name": "Updated Category",
            "parent_category": self.category.id  # 自分自身を親に設定
        }
        response = self.client.put(f"/api/categories/{self.category.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("自分自身を親カテゴリ", str(response.data))

    def test_create_circular_reference_error(self):
        # A -> B -> A の循環参照テスト
        category_a = Category.objects.create(
            company=self.company,
            name="Category A"
        )
        category_b = Category.objects.create(
            company=self.company,
            name="Category B",
            parent_category=category_a
        )

        # category_a の親を category_b に設定（循環参照）
        data = {
            "company": self.company.id,
            "name": "Category A",
            "parent_category": category_b.id
        }
        response = self.client.put(f"/api/categories/{category_a.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("循環参照", str(response.data))

    def test_create_different_company_parent_error(self):
        other_company = Company.objects.create(name="Other Company")
        parent_category = Category.objects.create(
            company=other_company,
            name="Other Company Category"
        )

        data = {
            "company": self.company.id,
            "name": "Child Category",
            "parent_category": parent_category.id
        }
        response = self.client.post("/api/categories/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("同じ企業に属している", str(response.data))

    def test_create_duplicate_name_error(self):
        # 同じ企業で同じ名前のカテゴリを作成
        data = {
            "company": self.company.id,
            "name": "Test Category"  # 既存のものと同じ名前
        }
        response = self.client.post("/api/categories/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("unique set", str(response.data))

    def test_update_duplicate_name_error(self):
        # 別のカテゴリを作成
        other_category = Category.objects.create(
            company=self.company,
            name="Other Category"
        )

        # 既存のカテゴリと同じ名前への更新を試行
        data = {
            "company": self.company.id,
            "name": "Test Category"  # 既存のものと同じ名前
        }
        response = self.client.put(f"/api/categories/{other_category.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("unique set", str(response.data))

    def test_destroy(self):
        response = self.client.delete(f"/api/categories/{self.category.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())
