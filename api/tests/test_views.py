from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Category, Company


class CategoryViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(name="テスト企業")

    def test_list(self):
        category_a = Category.objects.create(company=self.company, name="カテゴリA")
        category_b = Category.objects.create(company=self.company, name="カテゴリB")

        response = self.client.get("/api/categories/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {row["id"] for row in response.json()}
        self.assertEqual(ids, {str(category_a.id), str(category_b.id)})

    def test_retrieve(self):
        category = Category.objects.create(company=self.company, name="カテゴリA")

        response = self.client.get(f"/api/categories/{category.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        self.assertEqual(body["id"], str(category.id))
        self.assertEqual(body["company"], str(self.company.id))
        self.assertEqual(body["name"], "カテゴリA")
        self.assertIsNone(body["parent_category"])

    def test_retrieve_not_found(self):
        response = self.client.get("/api/categories/00000000-0000-0000-0000-000000000000/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create(self):
        payload = {"company": str(self.company.id), "name": "カテゴリA", "parent_category": None}

        response = self.client.post("/api/categories/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        body = response.json()
        self.assertEqual(body["company"], str(self.company.id))
        self.assertEqual(body["name"], "カテゴリA")
        self.assertIsNone(body["parent_category"])
        self.assertTrue(Category.objects.filter(id=body["id"]).exists())

    def test_create_with_parent_category(self):
        parent = Category.objects.create(company=self.company, name="親カテゴリ")
        payload = {"company": str(self.company.id), "name": "子カテゴリ", "parent_category": str(parent.id)}

        response = self.client.post("/api/categories/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["parent_category"], str(parent.id))

    def test_create_invalid(self):
        response = self.client.post("/api/categories/", {"name": ""}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update(self):
        category = Category.objects.create(company=self.company, name="カテゴリA")
        payload = {"company": str(self.company.id), "name": "カテゴリA-更新", "parent_category": None}

        response = self.client.put(f"/api/categories/{category.id}/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["name"], "カテゴリA-更新")
        category.refresh_from_db()
        self.assertEqual(category.name, "カテゴリA-更新")

    def test_update_not_found(self):
        payload = {"company": str(self.company.id), "name": "x", "parent_category": None}

        response = self.client.put(
            "/api/categories/00000000-0000-0000-0000-000000000000/", payload, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_destroy(self):
        category = Category.objects.create(company=self.company, name="カテゴリA")

        response = self.client.delete(f"/api/categories/{category.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=category.id).exists())
        self.assertEqual(
            self.client.get(f"/api/categories/{category.id}/").status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_destroy_not_found(self):
        response = self.client.delete("/api/categories/00000000-0000-0000-0000-000000000000/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
