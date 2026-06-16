import json

from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.test import APITestCase

from api.models import Category, Company
from api.serializers.category import CategorySerializer


class CategoryViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(name="テスト企業")

    def _category_response(self, category):
        return json.loads(JSONRenderer().render(CategorySerializer(category).data))

    def test_list(self):
        """正常系: カテゴリ一覧取得 一覧は作成した順に並んでいる"""
        category_a = Category.objects.create(company=self.company, name="カテゴリA")
        category_b = Category.objects.create(company=self.company, name="カテゴリB")

        response = self.client.get("/api/categories/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            [self._category_response(category_a), self._category_response(category_b)]
        )

    def test_retrieve(self):
        """正常系: カテゴリ詳細取得"""
        category = Category.objects.create(company=self.company, name="カテゴリA")

        response = self.client.get(f"/api/categories/{category.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), self._category_response(category))

    def test_retrieve_not_found(self):
        """異常系: 存在しないカテゴリ詳細取得は404エラー"""
        response = self.client.get("/api/categories/00000000-0000-0000-0000-000000000000/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create(self):
        """正常系: カテゴリ作成"""
        payload = {"company": str(self.company.id), "name": "カテゴリA", "parent_category": None}

        response = self.client.post("/api/categories/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        body = response.json()
        self.assertEqual(body["company"]["id"], str(self.company.id))
        self.assertEqual(body["company"]["name"], self.company.name)
        self.assertEqual(body["name"], "カテゴリA")
        self.assertIsNone(body["parent_category"])
        self.assertTrue(Category.objects.filter(id=body["id"]).exists())

    def test_create_with_parent_category(self):
        """正常系: 親カテゴリを指定してカテゴリ作成"""
        parent = Category.objects.create(company=self.company, name="親カテゴリ")
        payload = {"company": str(self.company.id), "name": "子カテゴリ", "parent_category": str(parent.id)}

        response = self.client.post("/api/categories/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["parent_category"], str(parent.id))

    def test_create_empty_name(self):
        """異常系: カテゴリ作成 nameが空の場合は400エラー"""
        payload = {"company": str(self.company.id), "name": "", "parent_category": None}

        response = self.client.post("/api/categories/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_missing_name(self):
        """異常系: カテゴリ作成 nameが未指定の場合は400エラー"""
        payload = {"company": str(self.company.id), "parent_category": None}

        response = self.client.post("/api/categories/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_name_too_long(self):
        """異常系: カテゴリ作成 nameが最大長を超える場合は400エラー"""
        payload = {"company": str(self.company.id), "name": "a" * 256, "parent_category": None}

        response = self.client.post("/api/categories/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_missing_company(self):
        """異常系: カテゴリ作成 companyが未指定の場合は400エラー"""
        payload = {"name": "カテゴリX", "parent_category": None}

        response = self.client.post("/api/categories/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_nonexistent_company(self):
        """異常系: カテゴリ作成 companyが存在しない場合は400エラー"""
        payload = {"company": "00000000-0000-0000-0000-000000000000", "name": "カテゴリX", "parent_category": None}

        response = self.client.post("/api/categories/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_company_format(self):
        """異常系: カテゴリ作成 companyがUUID形式でない場合は400エラー"""
        payload = {"company": "invalid-uuid", "name": "カテゴリX", "parent_category": None}

        response = self.client.post("/api/categories/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_nonexistent_parent_category(self):
        """異常系: カテゴリ作成 parent_categoryが存在しない場合は400エラー"""
        payload = {"company": str(self.company.id), "name": "カテゴリX", "parent_category": "00000000-0000-0000-0000-000000000000"}

        response = self.client.post("/api/categories/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_duplicate_company_name(self):
        """異常系: カテゴリ作成 companyとnameが重複する場合は400エラー"""
        Category.objects.create(company=self.company, name="重複カテゴリ")
        payload = {"company": str(self.company.id), "name": "重複カテゴリ", "parent_category": None}

        response = self.client.post("/api/categories/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update(self):
        """正常系: カテゴリ更新"""
        category = Category.objects.create(company=self.company, name="カテゴリA")
        payload = {"company": str(self.company.id), "name": "カテゴリA-更新", "parent_category": None}

        response = self.client.put(f"/api/categories/{category.id}/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["name"], "カテゴリA-更新")
        category.refresh_from_db()
        self.assertEqual(category.name, "カテゴリA-更新")

    def test_update_not_found(self):
        """異常系: 存在しないカテゴリ更新は404エラー"""
        payload = {"company": str(self.company.id), "name": "x", "parent_category": None}

        response = self.client.put(
            "/api/categories/00000000-0000-0000-0000-000000000000/", payload, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_missing_company(self):
        """異常系: カテゴリ更新 companyが未指定の場合は400エラー"""
        category = Category.objects.create(company=self.company, name="カテゴリA")
        payload = {"name": "カテゴリX", "parent_category": None}

        response = self.client.put(f"/api/categories/{category.id}/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_nonexistent_company(self):
        """異常系: カテゴリ更新 companyが存在しない場合は400エラー"""
        category = Category.objects.create(company=self.company, name="カテゴリA")
        payload = {"company": "00000000-0000-0000-0000-000000000000", "name": "カテゴリX", "parent_category": None}

        response = self.client.put(f"/api/categories/{category.id}/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_invalid_company_format(self):
        """異常系: カテゴリ更新 companyがUUID形式でない場合は400エラー"""
        category = Category.objects.create(company=self.company, name="カテゴリA")
        payload = {"company": "invalid-uuid", "name": "カテゴリX", "parent_category": None}

        response = self.client.put(f"/api/categories/{category.id}/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_missing_name(self):
        """異常系: カテゴリ更新 nameが未指定の場合は400エラー"""
        category = Category.objects.create(company=self.company, name="カテゴリA")
        payload = {"company": str(self.company.id), "parent_category": None}

        response = self.client.put(f"/api/categories/{category.id}/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_empty_name(self):
        """異常系: カテゴリ更新 nameが空の場合は400エラー"""
        category = Category.objects.create(company=self.company, name="カテゴリA")
        payload = {"company": str(self.company.id), "name": "", "parent_category": None}

        response = self.client.put(f"/api/categories/{category.id}/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_name_too_long(self):
        """異常系: カテゴリ更新 nameが最大長を超える場合は400エラー"""
        category = Category.objects.create(company=self.company, name="カテゴリA")
        payload = {"company": str(self.company.id), "name": "a" * 256, "parent_category": None}

        response = self.client.put(f"/api/categories/{category.id}/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_nonexistent_parent_category(self):
        """異常系: カテゴリ更新 parent_categoryが存在しない場合は400エラー"""
        category = Category.objects.create(company=self.company, name="カテゴリA")
        payload = {"company": str(self.company.id), "name": "カテゴリX", "parent_category": "00000000-0000-0000-0000-000000000000"}

        response = self.client.put(f"/api/categories/{category.id}/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_destroy(self):
        """正常系: カテゴリ削除"""
        category = Category.objects.create(company=self.company, name="カテゴリA")

        response = self.client.delete(f"/api/categories/{category.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=category.id).exists())
        self.assertEqual(
            self.client.get(f"/api/categories/{category.id}/").status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_destroy_not_found(self):
        """異常系: 存在しないカテゴリ削除は404エラー"""
        response = self.client.delete("/api/categories/00000000-0000-0000-0000-000000000000/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
